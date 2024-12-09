from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from admin_functions.forms import AllocationForm
from request_handler.models import Request, User, Venue
from user_system.models import Day, KnowledgeArea


class AllocateRequestView(LoginRequiredMixin, View):
    """Class-based view for the tutoring request allocation functionality.

    The AllocateRequestView allows an Admin user to allocate a request from a student whose current allocation status is
    set to "unallocated". This allocation takes into account all relevant factors: tutor expertise, student and tutor
    availability, etc.

    This class defines the acceptable HTTP methods for its URL and what the server should return to the client based on
    the method that was used.
    """

    def get(self, http_request, request_id):
        lesson_request = get_object_or_404(Request, id=request_id)

        if lesson_request.allocated:
            return render(http_request, 'already_allocated_error.html', status=409)

        student = lesson_request.student
        day1 = http_request.GET.get("day1", None)
        day2 = http_request.GET.get("day2", None)
        venue = http_request.GET.get('venue', None)
        venues = get_venue_preference(lesson_request.venue_preference)

        day1 = int(day1) if day1 else None
        day2 = int(day2) if day2 else None
        venue_id = int(venue) if venue else None

        form_data = {"day1": day1, "day2": day2, "venue": venue_id}
        if not day1 or (lesson_request.frequency == 'Biweekly' and not day2):
            form = AllocationForm(http_request.GET, initial=form_data, student=student, venues=venues)
        else:
            suitable_tutors = get_suitable_tutors(request_id, day1, day2)
            form = AllocationForm(http_request.GET, initial=form_data, student=student, venues=venues,
                                  tutors=suitable_tutors)

        venue_preferences = {"No Preference"} if len(venues) >= 2 else {
            venue.venue for venue in venues if venue.venue != "No Preference"
        }

        return render(http_request, "allocate_request.html", {
            "form": form,
            "day1": day1,
            "day2": day2,
            "venue": venue,
            "lesson_request": lesson_request,
            "venue_preferences": venue_preferences,
        })

    def post(self, request, request_id):
        lesson_request = get_object_or_404(Request, id=request_id)

        if lesson_request.allocated:
            return render(request, 'already_allocated_error.html', status=409)

        venues = get_venue_preference(lesson_request.venue_preference)
        day1 = request.POST.get("day1", None)
        day2 = request.POST.get("day2", None)

        day1_data = day1 if day1 and day1 != 'None' else None
        day2_data = day2 if day2 and day2 != 'None' else None

        if not day1_data:
            return HttpResponseBadRequest("Missing required day1", status=400)

        if lesson_request.frequency == "Biweekly" and not day2_data:
            return HttpResponseBadRequest("Missing required day2", status=400)

        day1_id = int(day1_data)
        day2_id = int(day2_data) if day2_data else None
        suitable_tutors = get_suitable_tutors(request_id, day1_id, day2_id)
        form = AllocationForm(request.POST, tutors=suitable_tutors, student=lesson_request.student, venues=venues)

        if lesson_request.frequency != "Biweekly":
            form.fields.pop('day2', None)

        if form.is_valid():
            tutor = form.cleaned_data.get('tutor')
            venue = form.cleaned_data.get('venue')

            if not tutor:
                form.add_error('tutor', "You must select a tutor!")
                return HttpResponseBadRequest("Missing required tutor")

            if not venue:
                form.add_error('venue', "You must select a venue!")
                return HttpResponseBadRequest("Missing required venue")

            day1 = Day.objects.get(id=day1_id) if day1_data else None
            day2 = Day.objects.get(id=day2_id) if day2_data else None
            _allocate(lesson_request, tutor, venue, day1, day2)
            _update_availabilities(lesson_request, day1, day2)
            return redirect("view_requests")

        venue_preferences = {"No Preference"} if len(venues) >= 2 else {
            venue.venue for venue in venues if venue.venue != "No Preference"
        }

        return render(request, "allocate_request.html", {
            "form": form,
            "lesson_request": lesson_request,
            "venue_preferences": venue_preferences,
        })

    def dispatch(self, request, *args, **kwargs):
        """Customise the dispatch method of the LoginRequiredMixin

        This function redirects an HTTP request from an unauthenticated user to the login page, and an authenticated
        user with insufficient privileges to a page where they are informed of their lack of permissions.
        """
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            return render(request, 'permission_denied.html', status=403)
        return super().dispatch(request, *args, **kwargs)


def get_venue_preference(venue_preference: QuerySet) -> QuerySet:
    if venue_preference.filter(venue='No Preference').exists():
        venues = Venue.objects.exclude(venue='No Preference')
    else:
        venues = venue_preference.all()
    return venues


def get_suitable_tutors(request_id: int, day1_id: int, day2_id: int) -> QuerySet:
    lesson_request = get_object_or_404(Request, id=request_id)

    if not day1_id:
        return User.objects.none()

    if lesson_request.frequency == 'Biweekly' and not day2_id:
        return User.objects.none()

    student = lesson_request.student
    knowledge_area = lesson_request.knowledge_area
    knowledge_area_ids = KnowledgeArea.objects.filter(subject=knowledge_area).values_list('id', flat=True)
    max_hourly_rate = student.student_max_rate

    if lesson_request.frequency == 'Biweekly':
        suitable_tutors = User.objects.filter(
            user_type="Tutor",
            knowledgearea__in=knowledge_area_ids,
            availability__in=Day.objects.filter(Q(id=day1_id) | Q(id=day2_id)),
            hourly_rate__lte=max_hourly_rate,
        ).distinct()
    else:
        suitable_tutors = User.objects.filter(
            user_type="Tutor",
            knowledgearea__in=knowledge_area_ids,
            availability__in=Day.objects.filter(id=day1_id),
            hourly_rate__lte=max_hourly_rate,
        ).distinct()

    return suitable_tutors


def _allocate(lesson_request: Request, tutor: User, venue: Venue, day1: Day, day2: Day) -> None:
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if lesson_request.frequency == 'Biweekly':# and weekdays.index(day1.day) < weekdays.index(day2.day):
        #Ensure day1 is before day2
        #lesson_request.day = day1
        lesson_request.day2 = day2
    #elif lesson_request.frequency == 'Biweekly' and weekdays.index(day1.day) > weekdays.index(day2.day):
    #    lesson_request.day = day2
    #    lesson_request.day2 = day1
    #else:
    #    lesson_request.day = day1

    lesson_request.tutor = tutor
    lesson_request.day = day1
    lesson_request.venue = venue
    lesson_request.allocated = True
    lesson_request.save()


def _update_availabilities(lesson_request: Request, day1: Day, day2: Day) -> None:
    if lesson_request.frequency == 'Biweekly':
        lesson_request.student.availability.remove(day2)
        lesson_request.tutor.availability.remove(day2)

    lesson_request.student.availability.remove(day1)
    lesson_request.tutor.availability.remove(day1)
    lesson_request.student.save()
    lesson_request.tutor.save()
    lesson_request.save()

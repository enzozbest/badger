from functools import partial

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.http import HttpResponseBadRequest
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from admin_functions.forms import AllocationForm
from request_handler.models.request_model import Request
from request_handler.models.venue_model import Venue
from user_system.models.day_model import Day
from user_system.models.knowledge_area_model import KnowledgeArea
from user_system.models.user_model import User


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

        student, day1, day2, venue, venues = get_required_data_get(lesson_request, http_request)
        day1 = int(day1) if day1 else None
        day2 = int(day2) if day2 else None
        venue_id = int(venue) if venue else None

        form_data = {"day1": day1, "day2": day2, "venue": venue_id}
        form = create_form_get(lesson_request, venues, form_data, student, http_request.GET, day1, day2)
        return render(http_request, "allocate_request.html", {
            "form": form,
            "day1": day1,
            "day2": day2,
            "venue": venue,
            "lesson_request": lesson_request,
            "venue_preferences": venue_preference_str(venues),
        })

    def post(self, http_request, request_id):
        lesson_request = get_object_or_404(Request, id=request_id)
        if lesson_request.allocated:
            return render(http_request, 'already_allocated_error.html', status=409)

        day1_data = get_day_data(http_request, 1)
        day2_data = get_day_data(http_request, 2)
        if not day1_data:
            return HttpResponseBadRequest("Missing required day1", status=400)
        if lesson_request.frequency == "Biweekly" and not day2_data:
            return HttpResponseBadRequest("Missing required day2", status=400)

        venues = get_venue_preference(lesson_request.venue_preference)
        day1_id = int(day1_data) if day1_data else None
        day2_id = int(day2_data) if day2_data else None
        form = create_form_post(lesson_request, day1_id, day2_id, venues, http_request.POST)

        valid_form = form.is_valid()
        if valid_form and process_allocation(form, lesson_request, day1_id, day2_id): 
            return HttpResponseBadRequest(form.errors)
        elif valid_form:
            return redirect("view_requests")
        else:
            return render(http_request, "allocate_request.html", {
                "form": form,
                "lesson_request": lesson_request,
                "venue_preferences": venue_preference_str(venues),
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


# -HELPERS- #
def get_required_data_get(lesson_request: Request, http_request: HttpRequest) -> tuple:
    """ Returns the data provided through the get request """
    student = lesson_request.student
    day1 = http_request.GET.get("day1", None)
    day2 = http_request.GET.get("day2", None)
    venue = http_request.GET.get('venue', None)
    venues = get_venue_preference(lesson_request.venue_preference)
    return student, day1, day2, venue, venues


def venue_preference_str(venues):
    return {"No Preference"} if len(venues) >= 2 else {
        venue.venue for venue in venues if venue.venue != "No Preference"
    }


def create_form_post(lesson_request, day1_id, day2_id, venues, http_data):
    suitable_tutors = get_suitable_tutors(lesson_request.id, day1_id, day2_id)
    form = AllocationForm(http_data, tutors=suitable_tutors, student=lesson_request.student, venues=venues)
    if lesson_request.frequency != "Biweekly":
        form.fields.pop('day2', None)
    return form


def create_form_get(lesson_request, venues, form_data, student, http_data, day1_id=None, day2_id=None):
    if not day1_id or (lesson_request.frequency == 'Biweekly' and not day2_id):
        suitable_tutors = None
    else:
        suitable_tutors = get_suitable_tutors(lesson_request.id, day1_id, day2_id)

    return AllocationForm(http_data, initial=form_data, student=student, venues=venues,
                          tutors=suitable_tutors)


def find_form_errors_post(form, tutor, venue):
    if not tutor:
        form.add_error('tutor', "Missing required tutor")
        return True
    if not venue:
        form.add_error('venue', "Missing required venue")
        return True
    return False


def get_day_data(http_request: HttpRequest, day_num: int):
    day = http_request.POST.get(f"day{day_num}", None)
    return day if (day and day != 'None') else None


def get_venue_preference(venue_preference: QuerySet) -> QuerySet:
    if venue_preference.filter(venue='No Preference').exists():
        venues = Venue.objects.exclude(venue='No Preference')
    else:
        venues = venue_preference.all()
    return venues


def get_suitable_tutors(request_id: int, day1_id: int, day2_id: int) -> QuerySet:
    """ Returns any tutors from the database which are suitable to be allocated to the request 
    Depends on their day availability, knowledge_areas and hourly rates
    """
    lesson_request = get_object_or_404(Request, id=request_id)
    if find_impediments(day1_id, lesson_request.frequency, day2_id):
        return User.objects.none()

    student = lesson_request.student
    knowledge_area = lesson_request.knowledge_area
    knowledge_area_ids = KnowledgeArea.objects.filter(subject=knowledge_area).values_list('id', flat=True)
    max_hourly_rate = student.student_max_rate

    availability_query = get_availability(lesson_request, day1_id, day2_id)

    return get_tutors(knowledge_area_ids, max_hourly_rate, availability_query)


def get_availability(lesson_request, day1_id, day2_id):
    if lesson_request.frequency == 'Biweekly':
        return partial(Day.objects.filter, Q(id=day1_id) | Q(id=day2_id))
    else:
        return partial(Day.objects.filter, id=day1_id)


def get_tutors(knowledge_area_ids, max_hourly_rate, availability_query):
    return User.objects.filter(
        user_type="Tutor",
        knowledgearea__in=knowledge_area_ids,
        availability__in=availability_query(),
        hourly_rate__lte=max_hourly_rate,
    ).distinct()


def find_impediments(day1_id, frequency, day2_id) -> bool:
    if (not day1_id) or (frequency == 'Biweekly' and not day2_id):
        return True
    return False


def get_grouped_requests(id):
    return Request.objects.filter(group_request_id=id).all()

def _allocate(lesson_request: Request, tutor: User, venue: Venue, day1: Day, day2: Day) -> None:
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if lesson_request.frequency == 'Biweekly' and weekdays.index(day1.day) < weekdays.index(day2.day):
        # Ensure day1 is before day2
        lesson_request.day = day1
        lesson_request.day2 = day2
    elif lesson_request.frequency == 'Biweekly' and weekdays.index(day1.day) > weekdays.index(day2.day):
        lesson_request.day = day2
        lesson_request.day2 = day1
    else:
        lesson_request.day = day1

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


def process_allocation(form, lesson_request, day1_id, day2_id):
    tutor = form.cleaned_data.get('tutor')
    venue = form.cleaned_data.get('venue')
    if find_form_errors_post(form, tutor, venue):
        return "Errors"
    else:
        day1 = Day.objects.get(id=day1_id) if day1_id else None
        day2 = Day.objects.get(id=day2_id) if day2_id else None
        requests = get_grouped_requests(lesson_request.group_request_id)
        for request in requests:
            _allocate(request, tutor, venue, day1, day2)
            _update_availabilities(request, day1, day2)
        return None
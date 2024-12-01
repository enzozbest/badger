from django.contrib.auth.mixins import LoginRequiredMixin
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
        lesson_request, suitable_tutors, venues = _get_tuple(request_id)

        if lesson_request.allocated:
            return render(http_request, 'already_allocated_error.html', status=409)

        form = AllocationForm(student=lesson_request.student, tutors=suitable_tutors, venues=venues)

        return render(http_request, "allocate_request.html", {
            "form": form,
            "lesson_request": lesson_request,
        })

    def post(self, request, request_id):
        lesson_request, suitable_tutors, venues = _get_tuple(request_id)
        if lesson_request.allocated:
            return render(request, 'already_allocated_error.html', status=409)

        form = AllocationForm(request.POST, student=lesson_request.student, tutors=suitable_tutors, venues=venues)
        if form.is_valid():
            tutor = form.cleaned_data['tutor']
            day = form.cleaned_data['day']
            venue = form.cleaned_data['venue']
            _allocate(lesson_request, tutor, Venue.objects.get(id=int(venue)), day)
            _update_availabilities(lesson_request, day)
            return redirect("view_requests")

        return render(request, "allocate_request.html", {
            "form": form,
            "lesson_request": lesson_request, })

    def dispatch(self, request, *args, **kwargs):
        """Customise the dispatch method of the LoginRequiredMixin

        This function redirects an HTTP request from an unauthenticated user to the login page, and an authenticated
        user with insufficient privileges to a page where they are informed of their lack of permissions.
        """
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            return render(request, 'permission_denied.html', status=401)
        return super().dispatch(request, *args, **kwargs)


def _get_tuple(request_id: int) -> tuple:
    lesson_request = get_object_or_404(Request, id=request_id)
    student = lesson_request.student
    knowledge_area = lesson_request.knowledge_area
    knowledge_area_ids = KnowledgeArea.objects.filter(subject=knowledge_area).values_list('id', flat=True)
    venue_preference = lesson_request.venue_preference

    suitable_tutors = User.objects.filter(
        user_type="Tutor",
        knowledgearea__in=knowledge_area_ids,
        availability__in=student.availability.all()
    ).distinct()

    venues = (
        venue_preference.objects.all()
        if venue_preference == "No Preference"
        else Venue.objects.all()
    )
    return lesson_request, suitable_tutors, venues


def _allocate(lesson_request: Request, tutor: User, venue: Venue, day: Day) -> None:
    lesson_request.tutor = tutor
    lesson_request.day = day
    lesson_request.venue = venue
    lesson_request.allocated = True
    lesson_request.save()


def _update_availabilities(lesson_request: Request, day: Day) -> None:
    lesson_request.student.availability.remove(day)
    lesson_request.tutor.availability.remove(day)
    lesson_request.student.save()
    lesson_request.tutor.save()
    lesson_request.save()

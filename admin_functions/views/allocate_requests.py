from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.shortcuts import reverse
from request_handler.models import Request, User, Venue
from admin_functions.forms import AllocationForm
from user_system.models import KnowledgeArea, Day


class AllocateRequestView(LoginRequiredMixin, View):
    def get(self, request, request_id):
        lesson_request, suitable_tutors, venues = get_tuple(request_id)

        if lesson_request.allocated:
            return render(request, 'already_allocated_error.html', status=409)

        form = AllocationForm(student=lesson_request.student, tutors=suitable_tutors, venues=venues)

        return render(request, "allocate_request.html", {
            "form": form,
            "lesson_request": lesson_request,
        })

    def post(self, request, request_id):
        lesson_request, suitable_tutors, venues = get_tuple(request_id)
        if lesson_request.allocated:
            return render(request, 'already_allocated_error.html', status=409)

        form = AllocationForm(request.POST, student=lesson_request.student, tutors=suitable_tutors, venues=venues)
        if form.is_valid():
            tutor = form.cleaned_data['tutor']
            day = form.cleaned_data['day']
            venue = form.cleaned_data['venue']
            allocate(lesson_request, tutor, Venue.objects.get(id=int(venue)), day)
            update_availabilities(lesson_request, day)
            return redirect("view_requests")

        return render(request, "allocate_request.html", {
            "form": form,
            "lesson_request": lesson_request,})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            return render(request, 'permission_denied.html', status=401)
        return super().dispatch(request, *args, **kwargs)

def get_tuple(id: int) -> tuple:
    lesson_request = get_object_or_404(Request, id=id)
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


def allocate(lesson_request: Request, tutor: User, venue: Venue, day: Day) -> None:
    lesson_request.tutor = tutor
    lesson_request.day = day
    lesson_request.venue = venue
    lesson_request.allocated = True
    lesson_request.save()

def update_availabilities(lesson_request: Request, day: Day) -> None:
    lesson_request.student.availability.remove(day)
    lesson_request.tutor.availability.remove(day)
    lesson_request.student.save()
    lesson_request.tutor.save()
    lesson_request.save()
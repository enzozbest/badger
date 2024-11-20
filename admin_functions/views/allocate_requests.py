from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from request_handler.models import Request, User, Venue
from admin_functions.forms import AllocationForm
from user_system.models import KnowledgeArea


class AllocateRequestView(LoginRequiredMixin, View):
    def get(self, request, request_id):
        lesson_request, suitable_tutors, venues = get_tuple(request_id)

        form = AllocationForm(student=lesson_request.student, tutors=suitable_tutors, venues=venues)

        return render(request, "allocate_request.html", {
            "form": form,
            "lesson_request": lesson_request,
        })

    def post(self, request, request_id):
        lesson_request, suitable_tutors, venues = get_tuple(request_id)

        form = AllocationForm(request.POST, student=lesson_request.student, tutors=suitable_tutors, venues=venues)
        if form.is_valid():
            tutor = form.cleaned_data['tutor']
            day = form.cleaned_data['day']
            venue = form.cleaned_data['venue']

            lesson_request.tutor = tutor
            lesson_request.day = day
            lesson_request.venue = Venue.objects.get(id=int(venue)) # Assuming Venue is stored as an FK
            lesson_request.save()

            #Calculate cost of request
            #In the future, this could be generate invoice or the admin could click a button later doing this
            price = calculate_cost(tutor, request_id)

            #Update availabilities:
            lesson_request.student.availability.remove(day)
            lesson_request.tutor.availability.remove(day)
            lesson_request.student.save()
            lesson_request.tutor.save()
            lesson_request.save()

            return redirect("view_requests")

        return render(request, "allocate_request.html", {
            "form": form,
            "lesson_request": lesson_request,})

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

    print("Suitable Tutors Queryset:", suitable_tutors)

    venues = (
        venue_preference.objects.all()
        if venue_preference == "No Preference"
        else Venue.objects.all()
    )
    return lesson_request, suitable_tutors, venues

def calculate_cost(tutor: User, request_id: int)-> int:
    #Cost = price * duration * occurence
    lesson = get_object_or_404(Request, id=request_id)
    duration = lesson.duration
    #We would need to calculate the number of sessions they are scheduled for and then multiply this
    #Rather than 15 since they would want an accurate number, we then also wouldn't need the occurence
    cost = tutor.hourly_rate * duration  * 15 #Assuming a 15 week term
    return cost

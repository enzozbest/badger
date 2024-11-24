from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from request_handler.models import Request, Booking

class AcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        lesson_request = get_object_or_404(Request, id=request_id, allocated=True, tutor=request.user)

        try:
            # Create a new Booking object based on the allocated request
            Booking.objects.create(
                tutor=request.user,
                student=lesson_request.student,
                knowledge_area=lesson_request.knowledge_area,
                venue=lesson_request.venue,
                day=lesson_request.day,
                term=lesson_request.term,
                frequency=lesson_request.frequency,
                duration=lesson_request.duration,
                late=lesson_request.late,
                is_recurring=lesson_request.is_recurring,
            )

            lesson_request.delete()

        except Exception as e:
            print(f"Error creating booking: {e}")


        return redirect('view_requests')
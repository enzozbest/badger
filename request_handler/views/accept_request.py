from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from request_handler.models import Request, Booking

class AcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        lesson_request = get_object_or_404(Request, id=request_id)

        if not request.user.is_tutor: # If logged-in user is not a tutor
            return render(request, 'permission_denied.html', status=403)

        if lesson_request.tutor != request.user: # If tutor assigned to request is not the same as logged-in user
            return render(request, 'permission_denied.html', status=403)

        lesson_request.allocated = True
        lesson_request.tutor = request.user
        lesson_request.save()

        # if not Booking.objects.filter(request=lesson_request).exists():
        Booking.objects.create(
            request=lesson_request,
            tutor=request.user,
            student=lesson_request.student,
            knowledge_area=lesson_request.knowledge_area,
            venue=lesson_request.venue_preference.first() if lesson_request.venue_preference.exists() else None,
            day=lesson_request.day,
            # start_date=lesson_request.start_date,
            # end_date=lesson_request.end_date,
            term=lesson_request.term,
        )

        lesson_request.delete()

        return redirect('view_requests')
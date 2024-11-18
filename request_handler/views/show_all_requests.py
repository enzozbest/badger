from request_handler.models import Request
from request_handler.helpers.request_filter import AllocationFilter
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

class AllRequestsView(LoginRequiredMixin, ListView):
    model = Request
    template_name = 'view_requests.html'
    context_object_name = 'requests'
    paginate_by = 20
    ordering = ['pk']
    filterset_class = AllocationFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        relevant_requests = queryset
        if self.request.user.is_student:
            relevant_requests = queryset.filter(student=self.request.user)
        if self.request.user.is_tutor:
            relevant_requests = queryset.filter(tutor=self.request.user)

        self.filterset = AllocationFilter(self.request.GET, queryset=relevant_requests)
        if self.filterset.is_valid():
            return self.filterset.qs
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset  # Pass the filter object to the template
        context['count'] = context['requests'].count()
        context['total'] = self.filterset.qs.count()
        context['user'] = self.request.user
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()  # Redirects to login page
        return super().dispatch(request, *args, **kwargs)
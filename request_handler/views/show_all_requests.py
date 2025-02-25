from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from admin_functions.helpers.mixins import SortingMixin
from request_handler.helpers.request_filter import RequestFilter
from request_handler.models.request_model import Request
from django.db.models import Value, Case, When
from django.db.models.fields import CharField


class AllRequestsView(LoginRequiredMixin, SortingMixin, ListView):
    """Class-based ListView to represent display a list of all relevant tutoring requests in the database

    This view displays a filterable, sortable, searchable list of all relevant requests present in the database.
    """

    model = Request
    template_name = 'view_requests.html'
    context_object_name = 'requests'
    paginate_by = 20
    filterset_class = RequestFilter
    valid_sort_fields = ['id', 'student__first_name', 'student__last_name', 'knowledge_area', 'allocated']

    def get_queryset(self):
        """Method that queries a user's user-related requests and adds field payment_status to queryset."""

        queryset = super().get_queryset()
        relevant_requests = queryset
        if self.request.user.is_student:
            relevant_requests = queryset.filter(student=self.request.user)
        if self.request.user.is_tutor:
            relevant_requests = queryset.filter(tutor=self.request.user)

        annotated_queryset = relevant_requests.annotate(
            paid_status=Case(
                When(invoice__payment_status=True, then=Value("Yes")),
                When(invoice__payment_status=False, then=Value("No")),
                output_field=CharField()
            )
        )

        self.filterset = RequestFilter(self.request.GET, queryset=annotated_queryset)
        if self.filterset.is_valid():
            queryset = self.filterset.qs

        return self.get_sorting_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['count'] = context['requests'].count()
        context['total'] = self.filterset.qs.count()
        context['user'] = self.request.user
        return context

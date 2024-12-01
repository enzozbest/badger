from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic import ListView

from admin_functions.helpers.filters import UserFilter
from user_system.models import User


class AllUsersView(LoginRequiredMixin, ListView):
    """Class-based ListView to display all users registered in the database.

    When entering the page, the user will see a paginated, sortable, filterable, searchable list of all users in the
    database. This is properly formatted.
    Only Admin users can have access to this page, so the dispatch method of LoginRequiredMixin is overridden to reflect
    that.
    """

    model = User
    template_name = 'view_users.html'
    context_object_name = 'users'
    paginate_by = 20
    ordering = ['pk']
    filterset_class = UserFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        if self.filterset.is_valid():
            return self.filterset.qs
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset  # Pass the filter object to the template
        context['count'] = context['users'].count()
        context['total'] = self.filterset.qs.count()
        return context

    def get(self, request, *args, **kwargs):
        # Fetch the queryset
        self.object_list = self.get_queryset()

        # Apply pagination manually
        paginator = Paginator(self.object_list, self.paginate_by)
        page = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            # Redirect to the last page if out of range
            last_page = paginator.num_pages
            return HttpResponseRedirect(f"{reverse('view_all_users')}?page={last_page}")

        # Set `object_list` for the context
        self.object_list = page_obj
        return super().get(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.user_type == 'Admin':
            return render(request, 'permission_denied.html', status=403)
        return super().dispatch(request, *args, **kwargs)

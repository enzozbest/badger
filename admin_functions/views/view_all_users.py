from django.contrib.auth.mixins import LoginRequiredMixin
from admin_functions.helpers.mixins import SortingMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.generic import ListView
from user_system.models import User
from admin_functions.helpers.filters import UserFilter
from django.http import HttpResponse
from django.shortcuts import reverse, render
from django.http import HttpResponseRedirect

class AllUsersView(LoginRequiredMixin, SortingMixin, ListView):
    model = User
    template_name = 'view_users.html'
    context_object_name = 'users'
    paginate_by = 20
    ordering = ['pk']
    filterset_class = UserFilter
    valid_sort_fields = ['email', 'first_name', 'last_name', 'user_type']


    def get_queryset(self):
        queryset = super().get_queryset()

        if hasattr(self, 'filterset_class'):
            self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
            if self.filterset.is_valid():
                queryset = self.filterset.qs

        return self.get_sorting_queryset(queryset)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset  # Pass the filter object to the template
        context['count'] = context['users'].count()
        context['total'] = self.filterset.qs.count() if hasattr(self, 'filterset') else self.get_queryset().count()
        context['current_sort'] = self.request.GET.get('sort', self.default_sort_field)  # 当前排序字段
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
            return render(request, 'permission_denied.html', status=401)
        return super().dispatch(request, *args, **kwargs)
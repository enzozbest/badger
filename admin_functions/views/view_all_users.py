from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.generic import ListView
from user_system.models import User
from admin_functions.helpers.filters import UserFilter
from django.http import HttpResponse
from django.shortcuts import reverse, render
from django.http import HttpResponseRedirect

class AllUsersView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'view_users.html'
    context_object_name = 'users'
    paginate_by = 20
    ordering = ['pk']
    filterset_class = UserFilter

    def get_queryset(self):
        # Get the base queryset
        queryset = super().get_queryset()

        # Apply the filter
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        if self.filterset.is_valid():
            queryset = self.filterset.qs

        # Apply sorting
        sort_field = self.request.GET.get('sort', 'pk')  # Default to 'pk'
        if sort_field:
            try:
                # Validate sort_field against the model's fields
                valid_fields = [field.name for field in User._meta.get_fields()]
                if sort_field.lstrip('-') in valid_fields:
                    queryset = queryset.order_by(sort_field)
            except Exception:
                pass  # Ignore invalid sort_field and fall back to default

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset  # Pass the filter object to the template
        context['count'] = context['users'].count()
        context['total'] = self.filterset.qs.count()
        context['current_sort'] = self.request.GET.get('sort', 'pk')  # Pass current sort field
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
"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from user_system import views as tutorial_views
from request_handler.views import create_request as create_request_view, small_views as request_handler_views
from request_handler.views import show_all_requests as view_requests_view
from request_handler.views import edit_request as edit_request_view
from request_handler.views import delete_request as delete_request_view
from admin_functions.views import view_all_users as view_all_users_view
from admin_functions.views import small_views as small_views_view
from admin_functions.views import make_user_admin as make_user_admin_view
from admin_functions.views import allocate_requests as allocate_requests_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tutorial_views.home, name='home'),
    path('dashboard/', tutorial_views.dashboard, name='dashboard'),
    path('log_in/', tutorial_views.LogInView.as_view(), name='log_in'),
    path('log_out/', tutorial_views.log_out, name='log_out'),
    path('password/', tutorial_views.PasswordView.as_view(), name='password'),
    path('profile/', tutorial_views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', tutorial_views.SignUpView.as_view(), name='sign_up'),
    path('create_request/', create_request_view.CreateRequestView.as_view(), name="create_request"),
    path('request_success/', request_handler_views.request_success, name="request_success"),
    path('view_requests/',view_requests_view.AllRequestsView.as_view(), name='view_requests'),
    path('edit_request/<int:pk>/', edit_request_view.EditRequestView.as_view(), name='edit_request'),
    path('request/<int:pk>/delete/', delete_request_view.DeleteRequestView.as_view(), name='delete_request'),
    path('delete_request/<int:pk>/confirm/', delete_request_view.ConfirmDeleteRequestView.as_view(), name='confirm_delete_request'),
    path('permission_denied/', request_handler_views.permission_denied, name='permission_denied'),
    path('processing_late_request/', request_handler_views.processing_late_request, name='processing_late_request'),
    path('admins/dashboard', small_views_view.admin_dash, name="admin_dash"),
    path('admins/view_all_users', view_all_users_view.AllUsersView.as_view(), name='view_all_users'),
    path('admins/make_admin/<int:pk>', make_user_admin_view.MakeUserAdmin.as_view(), name="make_admin"),
    path('admins/make_admin/<int:pk>/confirm', make_user_admin_view.ConfirmMakeUserAdmin.as_view(), name="confirm_make_admin"),
    path('add-knowledge-areas/', tutorial_views.AddKnowledgeAreas, name='add_knowledge_areas'),
    path('delete-knowledge-area/<int:area_id>/', tutorial_views.DeleteKnowledgeArea, name='delete_knowledge_area'),
    path("admins/allocate_request/<int:request_id>/", allocate_requests_view.AllocateRequestView.as_view(), name="allocate_request"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
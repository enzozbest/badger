from django.urls.conf import path

from .views.allocate_requests import AllocateRequestView
from .views.make_user_admin import ConfirmMakeUserAdmin, MakeUserAdmin
from .views.small_views import admin_dash
from .views.view_all_users import AllUsersView

urlpatterns = [
    path('dashboard/', admin_dash, name="admin_dash"),
    path('view_all_users/', AllUsersView.as_view(), name='view_all_users'),
    path('make_admin/<int:pk>/', MakeUserAdmin.as_view(), name="make_admin"),
    path('make_admin/<int:pk>/confirm/', ConfirmMakeUserAdmin.as_view(),
         name="confirm_make_admin"),
    path("allocate_request/<int:request_id>/", AllocateRequestView.as_view(),
         name="allocate_request"),
]

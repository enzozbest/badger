from django.urls.conf import path

from request_handler.views.create_request import CreateRequestView
from request_handler.views.delete_request import ConfirmDeleteRequestView, DeleteRequestView
from request_handler.views.edit_request import EditRequestView
from request_handler.views.show_all_requests import AllRequestsView
from request_handler.views.small_views import permission_denied, processing_late_request, request_success

urlpatterns = [
    path('create/', CreateRequestView.as_view(), name="create_request"),
    path('success/', request_success, name="request_success"),
    path('view/', AllRequestsView.as_view(), name='view_requests'),
    path('edit/<int:pk>/', EditRequestView.as_view(), name='edit_request'),
    path('delete/<int:pk>/', DeleteRequestView.as_view(), name='delete_request'),
    path('delete/<int:pk>/confirm/', ConfirmDeleteRequestView.as_view(),
         name='confirm_delete_request'),
    path('permission_denied/', permission_denied, name='permission_denied'),
    path('processing_late_request/', processing_late_request, name='processing_late_request'),
]

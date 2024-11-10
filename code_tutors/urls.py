"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views_dir. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views_dir
    1. Add an import:  from my_app import views_dir
    2. Add a URL to urlpatterns:  path('', views_dir.home, name='home')
Class-based views_dir
    1. Add an import:  from other_app.views_dir import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views as tutorial_views
from request_handler import views as request_handler_views
from request_handler.views_dir import create_request as create_request_view
from request_handler.views_dir import view_request as view_requests_view
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
    path('view_requests/',view_requests_view.ViewRequest.as_view(), name='view_requests'),
    path('edit_request/<int:pk>/', request_handler_views.edit_request, name='edit_request'),
    path('request/<int:pk>/delete/', request_handler_views.delete_request, name='delete_request'),
    path('delete_request/<int:pk>/confirm/', request_handler_views.confirm_delete_request, name='confirm_delete_request'),
    path('permission_denied/', request_handler_views.permission_denied, name='permission_denied'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
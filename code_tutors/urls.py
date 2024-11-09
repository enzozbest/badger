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
from tutorials import views as tutorial_views
from request_handler import views as request_handler_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tutorial_views.home, name='home'),
    path('dashboard/', tutorial_views.dashboard, name='dashboard'),
    path('log_in/', tutorial_views.LogInView.as_view(), name='log_in'),
    path('log_out/', tutorial_views.log_out, name='log_out'),
    path('password/', tutorial_views.PasswordView.as_view(), name='password'),
    path('profile/', tutorial_views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', tutorial_views.SignUpView.as_view(), name='sign_up'),
    path('create_request/', request_handler_views.create_request, name="create_request"),
    path('request_success/', request_handler_views.request_success, name="request_success"),
    path('view_requests/',request_handler_views.view_requests, name='view_requests'),
    path('edit_request/<int:pk>/', request_handler_views.edit_request, name='edit_request'),
    path('request/<int:pk>/delete/', request_handler_views.delete_request, name='delete_request'),
    path('delete_request/<int:pk>/confirm/', request_handler_views.confirm_delete_request, name='confirm_delete_request'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
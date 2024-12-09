from django.urls.conf import path

import user_system.views.login_view
import user_system.views.password_view
import user_system.views.profile_update_view
import user_system.views.sign_up_view
import user_system.views.small_views
from user_system.views.knowledge_area_views import add_knowledge_areas, delete_knowledge_area

urlpatterns = [path('', user_system.views.small_views.home, name='home'),
               path('dashboard/', user_system.views.small_views.dashboard, name='dashboard'),
               path('log_in/', user_system.views.login_view.LogInView.as_view(), name='log_in'),
               path('log_out/', user_system.views.small_views.log_out, name='log_out'),
               path('password/', user_system.views.password_view.PasswordView.as_view(), name='password'),
               path('profile/', user_system.views.profile_update_view.ProfileUpdateView.as_view(), name='profile'),
               path('sign_up/', user_system.views.sign_up_view.SignUpView.as_view(), name='sign_up'),
               path('add/knowledge/areas/', add_knowledge_areas,
                    name='add_knowledge_areas'),
               path('delete/knowledge/area/<int:area_id>/', delete_knowledge_area,
                    name='delete_knowledge_area'),
               ]

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import SingUpView, activate_user, update_profile, privacy_policy, terms_of_service
from .views import CustomLoginView  
from users.views import ResetPasswordView

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", SingUpView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html", next_page='home'), name="logout"),
    path('activate/<str:token>/<int:id>/', activate_user, name = 'activate'),
    path('password_reset/', ResetPasswordView.as_view(), name= 'password_reset'),
    path('update-profile', views.update_profile, name = 'update_profile'), 
    path('privacy-policy', views.privacy_policy, name = 'privacy_policy'),
    path('terms-of-service', views.terms_of_service, name = 'terms_of_service'),
]
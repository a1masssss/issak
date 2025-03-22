from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import SingUpView, activate_user
from .views import CustomLoginView  
from users.views import ResetPasswordView

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", SingUpView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html", next_page='login'), name="logout"),
    path('activate/<str:token>/<int:id>/', activate_user, name = 'activate'),
    path('password_reset/', ResetPasswordView.as_view(), name= 'password_reset'),


]
from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import UserRegisterForm
from django.shortcuts import redirect
from .models import EmailActivation, User
from django.views.generic import FormView   
from .forms import CustomAuthenticationForm
from django.contrib.auth import authenticate, login
import os 
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin


def home(request):
    return render(request, "users/base.html")

class SingUpView(CreateView):
    form_class = UserRegisterForm
    success_url = reverse_lazy("login")
    template_name = "users/register.html"


class CustomLoginView(FormView):
    template_name = "users/login.html"
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=email, password=password)

        if user: 
            activation = EmailActivation.objects.filter(user=user, is_active=True).first()
            if activation:
                login(self.request, user)
                return redirect('home')
            else:
                form.add_error(None, 'User is not activated')
                return self.form_invalid(form)
        else:
            form.add_error(None, "Incorrect pass or email") 
            return self.form_invalid(form)


def activate_user(request, token: str, id: int):
    activation = EmailActivation.objects.get(token=token)
    user = User.objects.get(id=id)
    activation.is_active = True
    activation.save()

    user.is_active = True 
    user.save()
    return redirect('login')




class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save(from_email='almas.issakov.t@gmail.com', request=self.request)
        return super().form_valid(form)





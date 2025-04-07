from functools import partial
from django.utils.crypto import get_random_string
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import send_mail
import uuid

get_random_token = partial(get_random_string, 100)

class UserManager(BaseUserManager):
    def get_by_natural_key(self, email):
        user = self.get(email=email)
        activation  = EmailActivation.objects.filter(user=user, is_active=True).first()
        if activation: 
            return user
        return None

class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['']

    objects = UserManager()

    def __str__(self):
        return self.email
    

class EmailActivation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token  = models.CharField(max_length=100, default=get_random_token)
    is_active = models.BooleanField(default=False)

    def send_email(self):
        subject = 'Activation Email'
        message = f'Activation link: http://localhost:8000/users/activate/{self.token}/{self.user.id}/'
        form_email = 'example@mail.com'
        recipient_list = [self.user.email]
        

        send_mail(subject, message, form_email, recipient_list, fail_silently=False)


        print('*' * 20)
        print('Email sent')
        print('*' * 20)







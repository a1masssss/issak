from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EmailActivation
from django.contrib.auth.forms import AuthenticationForm

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']
            

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label = ''

        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email',
            'class': 'form-control',
            'autocomplete': 'off'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })


    def save(self, commit=...):
        user: User = super().save(commit)
        if not user.is_active:
            activation = EmailActivation.objects.create(user=user)
            activation.send_email()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
            
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Email',
            'class': 'form-control',
            'autocomplete': ''
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'form-control',
            'autocomplete': 'new-password',
            'id': 'password'  # for hiding and showing password
        })

        for field in self.fields.values():
            field.label = ''



    username = forms.EmailField(label='Email')


class MyProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="", required = False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(label="", required = False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
    email = forms.EmailField(label="", required = True,  widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email')

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


    def save(self, commit=...):
        user = super().save(commit)
        print(f'Updated User: {user.email}, is_active={user.is_active}')
        if commit:
            user.save()
        return user
    

    
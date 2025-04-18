from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):

        user = super().save_user(request, user, form, commit=False)
        user.is_active = True 
        if commit:
            user.save()
        return user

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # This user is only a placeholder with the data from the social provider
        email = sociallogin.account.extra_data.get('email')

        if email:
            try:
                existing_user = User.objects.get(email=email)
                # Connect this social login to the existing user
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass  # No existing user, will proceed to create one

        # Activate new users if needed
        user = sociallogin.user
        if not user.pk:  
            user.is_active = True


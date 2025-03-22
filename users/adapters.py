from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """Ensure user is active for email/password signups."""
        user = super().save_user(request, user, form, commit=False)
        user.is_active = True  # Ensure activation
        if commit:
            user.save()
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Ensure user is active when signing up via Google."""
        user = sociallogin.user
        if not user.pk:  # If this is a new user (not in DB yet)
            user.is_active = True  # Set the user as active
            user.save()

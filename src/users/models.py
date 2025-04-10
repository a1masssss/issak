import datetime
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
    token = models.CharField(max_length=100, default=get_random_token)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Email Activation"
        verbose_name_plural = "Email Activations"
    
    def __str__(self):
        return f"Activation for {self.user.email}"
    
    def is_expired(self):
        """Check if the activation link has expired (24 hours)."""
        expiration_time = self.created_at + datetime.timedelta(hours=24)
        return datetime.timezone.now() > expiration_time
    
    def send_email(self):
        """Send a professional activation email to the user."""
        # Company name - change this to your actual company/app name
        company_name = "Issak"
        
    
        base_url = "http://localhost:8000/"  # Change to your production URL
        activation_url = f"{base_url}/users/activate/{self.token}/{self.user.id}/"
        
        # Email subject 
        subject = f'Activate Your {company_name} Account'
        
        # Create a professional HTML email body with proper formatting
        html_message = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Activation</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .logo {{
            max-height: 60px;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 30px;
            border-radius: 5px;
        }}
        .button {{
            display: inline-block;
            background-color: #4CAF50;
            color: white !important;
            text-decoration: none;
            padding: 12px 24px;
            margin: 20px 0;
            border-radius: 4px;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 12px;
            color: #777777;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <!-- Replace with your company logo -->
        <h1>{company_name}</h1>
    </div>
    <div class="content">
        <h2>Welcome to {company_name}!</h2>
        <p>Thank you for signing up. To complete your registration and activate your account, please click on the button below:</p>
        
        <div style="text-align: center;">
            <a href="{activation_url}" class="button">Activate Your Account</a>
        </div>
        
        <p>If the button above doesn't work, please copy and paste the following link into your web browser:</p>
        <p style="word-break: break-all;">{activation_url}</p>
        
        <p>This activation link will expire in 24 hours for security reasons.</p>
        
        <p>If you did not create an account with us, please disregard this email.</p>
        
        <p>Best regards,<br>
        The {company_name} Team</p>
    </div>
    <div class="footer">
        <p>This is an automated message. Please do not reply to this email.</p>
        <p>&copy; {datetime.datetime.now().year} {company_name}. All rights reserved.</p>
        <p><a href="{base_url}/privacy-policy">Privacy Policy</a> | <a href="{base_url}/terms">Terms of Service</a></p>
    </div>
</body>
</html>
'''
        
        # Plain text version for email clients that don't support HTML
        plain_message = f'''
Welcome to {company_name}!

Thank you for signing up. To complete your registration and activate your account, please visit the following link:

{activation_url}

This activation link will expire in 24 hours for security reasons.

If you did not create an account with us, please disregard this email.

Best regards,
The {company_name} Team

© {datetime.datetime.now().year} {company_name}. All rights reserved.
'''
        
        from_email = f'auth@{company_name.lower().replace(" ", "")}'
        
        # Recipient
        recipient_list = [self.user.email]
        
        # Send email with both HTML and plain text versions
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message
        )
        
        return True









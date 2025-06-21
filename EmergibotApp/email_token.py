from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings


def create_and_email_token(user_id):
    try:
        user = User.objects.get(id=user_id)

        # Create or retrieve the token
        token, _ = Token.objects.get_or_create(user=user)

        # Email the token to the user
        send_mail(
            subject='Your API Token',
            message=f'Hello {user.username},\n\nHere is your API token: {token.key}\n\nUse this token to access our APIs securely.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except User.DoesNotExist:
        return False

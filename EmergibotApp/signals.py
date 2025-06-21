from django.db.models.signals import post_save
from django.dispatch import receiver
from EmergibotApp.utils import get_client_ip
from EmergibotApp.models import ChatSession, UserToken
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_or_update_user_token(sender, instance, created, **kwargs):
    """Create or update a token whenever a user is saved."""
    if created:
        token = UserToken.objects.create(user=instance)
        token.send_token_email()  # Send token email on creation
    else:
        # Optionally regenerate the token and resend the email
        if hasattr(instance, 'custom_auth_token'):
            token = instance.custom_auth_token
            token.token = UserToken.generate_token()
            token.save()
            token.send_token_email()


@receiver(post_save, sender=ChatSession)
def log_chat_session_creation(sender, instance, created, **kwargs):
    """
    Log or handle additional logic when a ChatSession is created.
    """
    if created:
        pass

from datetime import datetime
from django.core.mail import EmailMessage
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import uuid

# Create your models here.
class ChatSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_closed = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Chat Session {self.session_id} - {self.ip_address}"
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-created_at']
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'

    def save(self, *args, **kwargs):
        self.session_id = str(uuid.uuid4().hex).upper()
        super(ChatSession, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def close(self):
        self.is_closed = True
        self.save()

    def archive(self):
        self.is_archived = True
        self.save()

class ChatMessage(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Message {self.id} - {self.session.session_id}"
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['-timestamp']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'

    def save(self, *args, **kwargs):
        # Ensure unique message_id
        if not self.message_id:
            self.message_id = str(uuid.uuid4().hex).upper()  # Generate a unique UUID

        self.user_message = self.user_message.lower()
        self.bot_response = self.bot_response.lower()
        super(ChatMessage, self).save(*args, **kwargs)

class UserToken(models.Model):
    token_id = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="custom_auth_token",  # Unique related name
    )
    token = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"

    @staticmethod
    def generate_token():
        """Generate a random 40-character token."""
        return get_random_string(40)

    def save(self, *args, **kwargs):
        """Override save to generate a token if not already set and send it via email."""
        if not self.token:
            self.token_id = str(uuid.uuid4().hex).upper()
            self.token = self.generate_token()
        super().save(*args, **kwargs)

        try:
            # Prepare the HTML email body

            html_body = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                
                <style>
                .token {{
                    width: 100%;
                    font-family: monospace;
                    font-size: 18px;
                    color: #2b2b2b;
                    background-color: #e8e8e8;
                    padding: 10px;
                    border-radius: 5px;
                    display: inline-block;
                }}
                </style>
            </head>
            <body style="margin: 0; padding: 20px; font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333;">
                <section style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); overflow: hidden;">
                    <header style="background-color: #4CAF50; padding: 20px; text-align: center; border-bottom: 4px solid #388E3C;">
                        <a href="https://emergimentors.com.au/" target="_blank">
                            <img src="https://i.ibb.co/wKMtbM2/image-1-1.png" alt="Emergi Mentors Logo" style="max-width: 150px;">
                        </a>
                    </header>

                    <main style="padding: 20px;">
                        <h2 style="color: #333333; font-size: 24px;">Hi {self.user.username},</h2>

                        <p style="margin: 20px 0; line-height: 1.6; color: #555;">
                            Welcome to <strong>Emergi Mentors</strong>! Below is your API token. Please keep it secure and use it to access our APIs.
                        </p>

                        <div>
                            <pre class="token">{self.token}</pre>
                        </div>

                        <p style="margin: 20px 0; line-height: 1.6; color: #555;">
                            If you have any questions or need further assistance, feel free to reach out to our support team.
                        </p>

                        <a href="https://emergimentors.com.au/" target="_blank" style="display: inline-block; padding: 10px 20px; margin: 20px 0; background-color: #4CAF50; color: white; text-decoration: none; font-weight: bold; border-radius: 5px;">
                            Visit Our Website
                        </a>
                    </main>

                    <footer style="padding: 20px; background-color: #f1f1f1; text-align: center; font-size: 14px; color: #777;">
                        <p>
                            This email was sent to <a href="mailto:{self.user.email}" style="color: #4CAF50; text-decoration: none;">{self.user.email}</a>.
                            If you'd rather not receive this kind of email, you can <a href="#!" style="color: #4CAF50; text-decoration: none;">unsubscribe</a>.
                        </p>
                        <p style="margin-top: 10px;">© {datetime.now().year} Emergi Mentors. All Rights Reserved.</p>
                    </footer>
                </section>
            </body>
            </html>
            """

            # Create and send the email
            email = EmailMessage(
                subject="Your API Token",
                body=html_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[self.user.email],
            )
            email.content_subtype = "html"  # Specify the email content type
            email.send(fail_silently=False)

            print(f"Token successfully sent to {self.user.email}")
        except Exception as e:
            raise ValueError(f"Error sending email: {e}")

    def send_token_email(self):
        self.save()



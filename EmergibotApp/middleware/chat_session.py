from EmergibotApp.models import ChatSession
from EmergibotApp.utils import get_client_ip
from django.utils.timezone import now


class ChatSessionMiddleware:
    """
    Middleware to create a ChatSession if it doesn't exist for the user's session key or IP.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure the user session exists
        if not request.session.session_key:
            request.session.create()

        # Retrieve session_id and IP address
        session_id = request.session.session_key
        ip_address = get_client_ip()

        # Check if a session with this IP address already exists
        existing_session = ChatSession.objects.filter(ip_address=ip_address).first()

        if not existing_session:
            # Create a new ChatSession if no existing record with this IP
            ChatSession.objects.get_or_create(
                session_id=session_id,
                defaults={
                    "ip_address": ip_address,
                    "created_at": now(),
                    "updated_at": now(),
                }
            )
            print(f"New ChatSession created: {session_id} for IP: {ip_address}")
        else:
            print(f"ChatSession already exists for IP: {ip_address}")

        response = self.get_response(request)
        return response

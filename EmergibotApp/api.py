import random
import humanize
from rest_framework.authentication import BaseAuthentication
from EmergibotApp.api_response_handler import APIResponseHandler
from EmergibotApp.models import ChatMessage, ChatSession, UserToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from EmergibotApp.utils import get_client_ip
from services.trainer import categorize_response, classify_sentence_type, get_response, preprocess_data




###########################################################

class TokenAuthentication(BaseAuthentication):
    """Custom token authentication for APIs."""

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Token "):
            return None

        token = auth_header.split("Token ")[-1]
        try:
            user_token = UserToken.objects.get(token=token)
            return user_token.user, None
        except UserToken.DoesNotExist:
            return None

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def protected_api(request):
    return APIResponseHandler.HTTP_200_OK(data={"message": f"Hello, {request.user.username}! This is a protected API."})


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chat_response_api(request):
    """
    Handle chat responses and fetch chat history for the current IP address.
    """
    ip_address = get_client_ip()
    print(f"IP Address: {ip_address}")

    if request.method == "POST":
        user_message = request.data.get("question")
        if not user_message:
            return APIResponseHandler().HTTP_400_BAD_REQUEST(errors="Question is required.")

        bot_response = get_response(user_message, ip_address)

        return APIResponseHandler().HTTP_200_OK(
            message="Message sent successfully",
            data={
                "messages": [
                    {
                        "user_message": user_message,
                        "bot_response": None,
                    },
                    {
                        "user_message": None,
                        "bot_response": bot_response["response"],
                    },
                ]
            },
        )

    elif request.method == "GET":
        # Fetch chat history for the given IP address
        session = ChatSession.objects.filter(ip_address=ip_address).first()
        if not session:
            return APIResponseHandler().HTTP_404_NOT_FOUND(message="No chat history found.")

        # Fetch and format chat history
        chats = ChatMessage.objects.filter(session=session).order_by("timestamp")
        chat_data = []
        for chat in chats:
            meta = {
                "sentence_type": classify_sentence_type(chat.bot_response),
                "response_category": categorize_response(chat.bot_response)
            }
            chat_data.append({
                "user_message": chat.user_message,
                "bot_response": chat.bot_response,
                "meta": meta,
                "timestamp": humanize.naturaltime(chat.timestamp),
            })

        # Build response for chat history
        return APIResponseHandler().HTTP_200_OK(data={
            "session_id": session.session_id,
            "ip_address": session.ip_address,
            "messages": chat_data,
        })


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def load_random_questions_from_files(request):
    """
    API to load 6–8 random questions from the knowledge base.
    """
    try:
        # Load and preprocess the data
        knowledge_base = preprocess_data()

        # Extract questions from the knowledge base
        questions = [entry["question"] for entry in knowledge_base]

        # Shuffle and select 6–8 random questions
        random_questions = random.sample(questions, k=min(len(questions), 4))

        return APIResponseHandler().HTTP_200_OK(data={"questions": random_questions})

    except FileNotFoundError as e:
        return APIResponseHandler().HTTP_404_NOT_FOUND(message=f"File not found: {str(e)}")

    except Exception as e:
        return APIResponseHandler().HTTP_500_INTERNAL_SERVER_ERROR(message=f"An error occurred: {str(e)}")
















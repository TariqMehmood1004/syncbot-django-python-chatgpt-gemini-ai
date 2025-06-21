from EmergibotApp.utils import get_client_ip
from EmergibotProject import settings
from django.shortcuts import render
import requests
import markdown
from services.trainer import get_response

############################# 

def render_markdown(text):
    """
    Convert markdown text to HTML for frontend rendering.
    """
    if not text:
        return ""
    
    # Configure markdown with extensions for better rendering
    md = markdown.Markdown(extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists'
    ])
    
    return md.convert(text)

def process_chat_messages(messages):
    """
    Process chat messages to convert markdown to HTML.
    """
    if not messages:
        return messages
    
    processed_messages = []
    for message in messages:
        processed_message = message.copy()
        
        # Convert bot responses from markdown to HTML
        if 'bot_response' in processed_message and processed_message['bot_response']:
            if isinstance(processed_message['bot_response'], dict):
                # If bot_response is a dict with 'response' key
                if 'response' in processed_message['bot_response']:
                    processed_message['bot_response']['response_html'] = render_markdown(
                        processed_message['bot_response']['response']
                    )
            else:
                # If bot_response is a string
                processed_message['bot_response_html'] = render_markdown(
                    processed_message['bot_response']
                )
        
        processed_messages.append(processed_message)
    
    return processed_messages

def chat_home(request):
    """
    Main chat page handling session initialization, query submission, and chat rendering via API.
    """
    if not request.session.session_key:
        request.session.create()

    ip_address = get_client_ip()

    # Retrieve chat history via API
    chat_history_response = requests.get(
        f"{settings.API_BASE_URL}/chat-response/",
        headers={"Authorization": f"Token {settings.API_AUTH_TOKEN}"},
    )
    if chat_history_response.status_code == 200:
        chat_history = chat_history_response.json().get("data", {}).get("messages", [])
        # Process messages for markdown rendering
        chat_history = process_chat_messages(chat_history)
    else:
        chat_history = []

    # Handle HTMX form submission
    if request.htmx:
        print("HTMX request detected: ", request.htmx)
        user_query = request.POST.get("question", "")
        if user_query:
            api_response = requests.post(
                f"{settings.API_BASE_URL}/chat-response/",
                json={"question": user_query},
                headers={"Authorization": f"Token {settings.API_AUTH_TOKEN}"},
            )
            if api_response.status_code == 200:
                bot_response = api_response.json().get("data", {}).get("messages", [])
                # Process messages for markdown rendering
                bot_response = process_chat_messages(bot_response)
                return render(request, "chat_snippets.html", {"chats": bot_response})

    # Render the chat page
    return render(request, "chat.html", {"chats": chat_history})

def load_chats(request):
    """
    Load chat history dynamically for the current session via API.
    """
    if not request.session.session_key:
        request.session.create()

    ip_address = get_client_ip()

    # Fetch chat history from the API
    chat_history_response = requests.get(
        f"{settings.API_BASE_URL}/chat-response/",
        headers={
            "Authorization": f"Token {settings.API_AUTH_TOKEN}",
            "X-IP-Address": ip_address,  # Include the user's IP address
        },
    )
    
    if chat_history_response.status_code == 200:
        chats = chat_history_response.json().get("data", {}).get("messages", [])
        # Process messages for markdown rendering
        chats = process_chat_messages(chats)
    else:
        chats = []

    # Fetch random questions if no chat history
    random_questions = []
    if not chats:
        random_questions_response = requests.get(
            f"{settings.API_BASE_URL}/load-random-questions-from-files/",
            headers={"Authorization": f"Token {settings.API_AUTH_TOKEN}"},
        )
        if random_questions_response.status_code == 200:
            random_questions = random_questions_response.json().get("data", {}).get("questions", [])

            # Debugging: Print fetched random questions
            for i, question in enumerate(random_questions):
                print(f"question-{i}: {question}")

    return render(request, "chat_snippets.html", {"chats": chats, "random_questions": random_questions})

def chat_response(request):
    """
    Handle HTMX requests for submitting a query and returning a chat snippet.
    """
    user_message = request.POST.get("question")
    ip_address = get_client_ip()

    if user_message:
        bot_response = get_response(user_message, ip_address)
        
        # Create messages array and process for markdown
        messages = [
            {
                "user_message": user_message, 
                "bot_response": None
            },
            {
                "user_message": None, 
                "bot_response": bot_response
            },
        ]
        
        # Process messages for markdown rendering
        processed_messages = process_chat_messages(messages)
        
        return render(request, "chat_snippets.html", {
            "messages": processed_messages
        })
    return render(request, "chat_snippets.html", {"messages": []})


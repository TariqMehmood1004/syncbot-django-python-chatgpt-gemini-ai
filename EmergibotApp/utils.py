import re
from urllib.parse import urlparse
from random import choice
from socket import gethostname, gethostbyname

def extract_links(text):
    url_pattern = r'(https?://[^\s]+)'
    raw_links = re.findall(url_pattern, text)

    cleaned_links = []
    for link in raw_links:
        cleaned_link = link.replace('"', '').strip()
        parsed = urlparse(cleaned_link)
        if parsed.scheme in ["http", "https"] and parsed.netloc:
            cleaned_links.append(cleaned_link)

    return cleaned_links

def get_client_ip():
    return gethostbyname(gethostname())

def chatbot_fallback_response():
    return "I'm sorry, I can only respond to your prompts about Emergi Mentors. Please let me know how I can help! 😊"

def format_responses(answer):
    return answer.replace("📌", "📌").replace("✔", "- ✔").replace("💡", "💡").replace(".", ".")

def welcome_message():
    return """
    👋 Hello! Welcome to EmergiBot. Here’s how I can assist:
    - Learn about mentorship.
    - Ask questions about the signup process.
    - Discover mentorship benefits.
    Feel free to ask anything! 😊
    """

def generate_response_variations(answer):
    return [
        answer,
        f"Here are the steps: \n{answer}",
        f"To complete the process: \n{answer}",
        f"To get started, \n{answer}",
    ]



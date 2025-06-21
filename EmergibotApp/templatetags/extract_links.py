import re
from urllib.parse import urlparse
from django import template

# Function to extract and clean URLs from any markdown-like response
def extract_links(text):
    """
    Extract and clean URLs from the text using regex.
    Works with Markdown links, raw URLs, or HTML-embedded links.
    """
    url_pattern = r'(https?://[^\s\)\]\">]+)'  # Match raw and markdown-style URLs
    raw_links = re.findall(url_pattern, text)

    cleaned_links = []
    for link in raw_links:
        cleaned_link = link.replace('"', '').strip()
        parsed = urlparse(cleaned_link)
        if parsed.scheme in ["http", "https"] and parsed.netloc:
            cleaned_links.append(cleaned_link)

    return cleaned_links


register = template.Library()
register.filter('extract_links', extract_links)


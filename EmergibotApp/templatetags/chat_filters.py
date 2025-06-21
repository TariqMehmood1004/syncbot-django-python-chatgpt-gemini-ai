import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name="simple_markdown")
def simple_markdown(value):
    """
    A very basic markdown renderer supporting:
    - bold: **text**
    - italic: _text_
    - links: [text](url)
    """
    if not value:
        return ""

    # Convert **bold**
    value = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", value)
    
    # Convert _italic_
    value = re.sub(r"_(.*?)_", r"<em>\1</em>", value)
    
    # Convert [text](url)
    value = re.sub(
        r"\[(.*?)\]\((https?://[^\s]+)\)",
        r'<a href="\2" target="_blank" class="text-blue-500 underline">\1</a>',
        value,
    )

    return mark_safe(value)

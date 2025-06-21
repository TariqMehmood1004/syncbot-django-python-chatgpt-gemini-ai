from django import template
import re
from django.utils.safestring import mark_safe



register = template.Library()

@register.filter
def add_target_blank(value):
    """
    Adds target="_blank" to all <a> tags in the given HTML string.
    """
    return re.sub(r'(<a .*?)>', r'\1 target="_blank">', value)


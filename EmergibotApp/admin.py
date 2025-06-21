from django.contrib import admin
from .models import ChatSession, ChatMessage, UserToken

# Register your models here.
admin.site.register(ChatSession)
admin.site.register(ChatMessage)
admin.site.register(UserToken)


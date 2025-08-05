from django.contrib import admin

from .models import ChartData, ChatMessage, ClaudeImage, GptImage, ImageLearnContent

# Register your models here.
admin.site.register(ImageLearnContent)
admin.site.register(ChartData)
admin.site.register(GptImage)
admin.site.register(ClaudeImage)
admin.site.register(ChatMessage)
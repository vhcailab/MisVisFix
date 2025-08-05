from django.db import models

class ImageLearnContent(models.Model):
    image_hash = models.CharField(max_length=255, db_index=True)  # Unique identifier for an image
    content = models.TextField()  # Stores the content associated with the image
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"Hash: {self.image_hash} - Content: {self.learn_content[:50]}"

class ChartData(models.Model):
    original_image = models.URLField()
    key_issues = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    gpt_solved_list = models.JSONField(null=True, blank=True)
    claude_solved_list = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"Chart {self.id}"


class GptImage(models.Model):
    chart = models.ForeignKey(ChartData, related_name='gpt_images', on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='gpt/', null=True, blank=True)

    def __str__(self):
        return f"GPT Image for Chart {self.chart.id}"


class ClaudeImage(models.Model):
    chart = models.ForeignKey(ChartData, related_name='claude_images', on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='claude/', null=True, blank=True)

    def __str__(self):
        return f"Claude Image for Chart {self.chart.id}"


class ChatMessage(models.Model):
    chart = models.ForeignKey(ChartData, related_name='chats', on_delete=models.CASCADE)
    user = models.CharField(max_length=50)  # e.g., "You", "AI"
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    issues = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Chat by {self.user} on Chart {self.chart.id}"

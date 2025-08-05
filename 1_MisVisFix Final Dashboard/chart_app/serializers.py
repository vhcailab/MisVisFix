from rest_framework import serializers
from .models import ImageLearnContent

class ImageLearnContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLearnContent
        fields = ['id', 'image_hash', 'content', 'created_at']  # Fields returned in API

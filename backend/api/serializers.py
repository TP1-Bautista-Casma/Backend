from rest_framework import serializers
from .models import ColorblindImage

class ColorblindImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorblindImage
        fields = ['id', 'image', 'type', 'subtype', 'uploaded_at']
        read_only_fields = ['uploaded_at']

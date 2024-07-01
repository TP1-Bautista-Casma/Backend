# serializers.py 
from rest_framework import serializers
from .models import User, ColorblindImage

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id','email', 'password']
        

    def create(self, validated_data):
        user = User(
            #username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ColorblindImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorblindImage
        fields = ['id', 'user', 'image', 'type', 'subtype', 'uploaded_at']
        read_only_fields = ['user', 'uploaded_at']
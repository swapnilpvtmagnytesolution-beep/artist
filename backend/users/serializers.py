from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import EventClient

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 
                  'profile_picture', 'password', 'is_active', 'date_joined')
        read_only_fields = ('id', 'is_active', 'date_joined')
    
    def validate_password(self, value):
        """Validate the password using Django's password validation."""
        validate_password(value)
        return value
    
    def create(self, validated_data):
        """Create a new user with encrypted password."""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update a user, setting the password correctly if present."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user data in the token response."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data.update({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
            }
        })
        return data


class EventClientSerializer(serializers.ModelSerializer):
    """Serializer for the EventClient model."""
    
    class Meta:
        model = EventClient
        fields = ('id', 'name', 'email', 'phone_number', 'created_at')
        read_only_fields = ('id', 'created_at')


class EventLoginSerializer(serializers.Serializer):
    """Serializer for event login using event ID and password."""
    event_id = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
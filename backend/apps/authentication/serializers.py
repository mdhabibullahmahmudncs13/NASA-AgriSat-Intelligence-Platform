from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile management.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_staff')
        read_only_fields = ('id', 'username', 'date_joined', 'is_staff')
    
    def validate_email(self, value):
        user = self.instance
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

class CustomAuthTokenSerializer(serializers.Serializer):
    """
    Custom serializer for authentication that accepts username or email.
    """
    username_or_email = serializers.CharField(label="Username or Email")
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')
        
        if username_or_email and password:
            # Try to authenticate with username first
            user = authenticate(request=self.context.get('request'),
                              username=username_or_email, password=password)
            
            # If authentication failed, try with email
            if not user:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request=self.context.get('request'),
                                      username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = 'User account is disabled.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username_or_email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
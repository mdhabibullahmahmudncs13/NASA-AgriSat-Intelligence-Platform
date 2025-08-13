from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, UserProfileSerializer, CustomAuthTokenSerializer

class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication token view that returns user data along with token.
    """
    serializer_class = CustomAuthTokenSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined,
                'is_staff': user.is_staff,
            }
        })

class UserRegistrationView(generics.CreateAPIView):
    """
    User registration view.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined,
            },
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view for retrieving and updating user information.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout view that deletes the user's token.
    """
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({
            'message': 'Token not found'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Change user password.
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response({
            'error': 'Both old_password and new_password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(old_password):
        return Response({
            'error': 'Old password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(new_password) < 8:
        return Response({
            'error': 'New password must be at least 8 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    # Delete old token and create new one
    try:
        token = Token.objects.get(user=user)
        token.delete()
    except Token.DoesNotExist:
        pass
    
    new_token = Token.objects.create(user=user)
    
    return Response({
        'message': 'Password changed successfully',
        'token': new_token.key
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """
    Get user statistics including farms, fields, and alerts count.
    """
    user = request.user
    
    # Import here to avoid circular imports
    from apps.fields.models import Farm, Field, Alert
    
    farms_count = Farm.objects.filter(owner=user).count()
    fields_count = Field.objects.filter(farm__owner=user).count()
    active_alerts = Alert.objects.filter(
        field__farm__owner=user,
        is_resolved=False
    ).count()
    
    return Response({
        'farms_count': farms_count,
        'fields_count': fields_count,
        'active_alerts': active_alerts,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
        }
    }, status=status.HTTP_200_OK)
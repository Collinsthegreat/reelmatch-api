from rest_framework import generics, permissions
from .models import User
from .serializers import UserSerializer

class UserListView(generics.ListAPIView):
    """
    Get a list of all users (only for authenticated users).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserDetailView(generics.RetrieveAPIView):
    """
    Get details of a single user by ID.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

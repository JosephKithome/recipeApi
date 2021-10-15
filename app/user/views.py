from django.shortcuts import render

from user.serializers import UserSerializer,TokenAuthSerializer
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = TokenAuthSerializer 
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES   
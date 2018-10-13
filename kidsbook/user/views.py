from django.shortcuts import render
from kidsbook.models import *
from kidsbook.serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.auth.models import User
from rest_framework import permissions
from profanity import profanity

from django.http import (
    HttpResponse, HttpResponseNotFound, JsonResponse
)
from django.contrib.auth import (
    authenticate, login, logout
)

from django.contrib.auth import get_user_model, get_user

class GetInfo(generics.ListAPIView):
    serializer_class = UserSerializer
    def list(self, request):
        current_user = get_user(request)
        serializer = UserSerializer(current_user, many=False)
        return Response(serializer.data)

class GetPost(generics.ListAPIView):
  queryset = ''
  serializer_class = PostSerializer
  def list(self, request):
    current_user = get_user(request)
    posts = Post.objects.filter(creator=current_user)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

# Create your views here.

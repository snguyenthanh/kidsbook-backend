from kidsbook.models import *
from kidsbook.serializers import *
from kidsbook.permissions import *
from rest_framework import generics, status
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
User = get_user_model()

class GroupPostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsInGroup,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(group = Group.objects.get(id=kwargs['group_id']))
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

class PostLike(generics.ListCreateAPIView):
    queryset = UserLikePost.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = (HasAccessToPost,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['post_id']))
        serializer = PostLikeSerializer(queryset, many=True)
        return Response(serializer.data)

class PostFlag(generics.ListCreateAPIView):
    queryset = UserFlagPost.objects.all()
    serializer_class = PostFlagSerializer
    permission_classes = (HasAccessToPost,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['post_id']))
        serializer = PostFlagSerializer(queryset, many=True)
        return Response(serializer.data)

class PostShare(generics.ListCreateAPIView):
    queryset = UserSharePost.objects.all()
    serializer_class = PostShareSerializer
    permission_classes = (HasAccessToPost,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['post_id']))
        serializer = PostShareSerializer(queryset, many=True)
        return Response(serializer.data)

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsSuperUser, HasAccessToPost)

class CompletePostDetail(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = CompletePostSerializer
    permission_classes = (IsSuperUser, HasAccessToPost)

class PostCommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (HasAccessToPost,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post=Post.objects.get(id=kwargs['post_id']))
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsSuperUser, HasAccessToComment)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUser,)

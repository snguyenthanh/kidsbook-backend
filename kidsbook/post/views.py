from kidsbook.models import *
from kidsbook.serializers import *
from kidsbook.permissions import *
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.permissions import IsAuthenticated

from django.http import (
    HttpResponse, HttpResponseNotFound, JsonResponse
)
from django.contrib.auth import (
    authenticate, login, logout
)

from django.contrib.auth import get_user_model, get_user
User = get_user_model()

class GroupPostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsInGroup)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(group = Group.objects.get(id=kwargs['pk']))
            serializer = PostSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception:
            return Response('Group not found', status=status.HTTP_404_NOT_FOUND)

class PostLike(generics.ListAPIView):
    queryset = UserLikePost.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = (IsAuthenticated, HasAccessToPost,)

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        serializer = PostLikeSerializer(queryset, many=True)
        return Response(serializer.data)

class CommentLike(generics.ListAPIView):
    queryset = UserLikeComment.objects.all()
    serializer_class = CommentLikeSerializer
    permission_classes = (IsAuthenticated, HasAccessToComment)

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(comment = Comment.objects.get(id=kwargs['pk']))
        serializer = CommentLikeSerializer(queryset, many=True)
        return Response(serializer.data)

class PostFlag(generics.ListAPIView):
    queryset = UserFlagPost.objects.all()
    serializer_class = PostFlagSerializer
    permission_classes = (IsAuthenticated, HasAccessToPost)

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        serializer = PostFlagSerializer(queryset, many=True)
        return Response(serializer.data)

class CommentFlag(generics.ListAPIView):
    queryset = UserFlagPost.objects.all()
    serializer_class = CommentFlagSerializer
    permission_classes = (IsAuthenticated, HasAccessToComment)

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(comment = Comment.objects.get(id=kwargs['pk']))
        serializer = CommentFlagSerializer(queryset, many=True)
        return Response(serializer.data)

class PostShare(generics.ListAPIView):
    queryset = UserSharePost.objects.all()
    serializer_class = PostShareSerializer
    permission_classes = (IsAuthenticated, HasAccessToPost,)

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        serializer = PostShareSerializer(queryset, many=True)
        return Response(serializer.data)

class PostDetail(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsSuperUser, HasAccessToPost)

    def list(self, request, **kwargs):
        queryset = self.get_queryset().get(id=kwargs['pk'])
        serializer = PostSerializer(queryset)
        return Response(serializer.data)

class CompletePostDetail(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = CompletePostSerializer
    permission_classes = (IsSuperUser, HasAccessToPost)

    def list(self, request, **kwargs):
        queryset = self.get_queryset().get(id=kwargs['pk'])
        serializer = PostSerializer(queryset)
        return Response(serializer.data)

class PostCommentList(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, HasAccessToPost)

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post=Post.objects.get(id=kwargs['pk']))
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

class CommentDetail(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsSuperUser, HasAccessToComment)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUser,)

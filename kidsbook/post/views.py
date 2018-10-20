from kidsbook.models import *
from kidsbook.serializers import *
from kidsbook.permissions import *
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated

from django.http import (
    HttpResponse, HttpResponseNotFound, JsonResponse
)
from django.contrib.auth import (
    authenticate, login, logout
)

from django.contrib.auth import get_user_model, get_user
from rest_framework.permissions import IsAuthenticated, AllowAny

User = get_user_model()

class GroupPostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsInGroup)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(group = Group.objects.get(id=kwargs['pk']))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = PostSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PostLike(generics.ListCreateAPIView):
    queryset = UserLikePost.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = (IsAuthenticated, HasAccessToPost,)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = PostLikeSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CommentLike(generics.ListCreateAPIView):
    queryset = UserLikeComment.objects.all()
    serializer_class = CommentLikeSerializer
    permission_classes = (IsAuthenticated, HasAccessToComment)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(comment = Comment.objects.get(id=kwargs['pk']))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = CommentLikeSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        # try:
            return Response({'data': self.create(request, *args, **kwargs).data})
        # except Exception:
            # return Response(status=status.HTTP_400_BAD_REQUEST)

class PostFlag(generics.ListCreateAPIView):
    queryset = UserFlagPost.objects.all()
    serializer_class = PostFlagSerializer
    permission_classes = (IsAuthenticated, HasAccessToPost)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = PostFlagSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        # try:
            return Response({'data': self.create(request, *args, **kwargs).data})
        # except Exception:
            # return Response(status=status.HTTP_400_BAD_REQUEST)

class CommentFlag(generics.ListCreateAPIView):
    queryset = UserFlagPost.objects.all()
    serializer_class = CommentFlagSerializer
    permission_classes = (IsAuthenticated, HasAccessToComment)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(comment = Comment.objects.get(id=kwargs['pk']))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = CommentFlagSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PostShare(generics.ListCreateAPIView):
    queryset = UserSharePost.objects.all()
    serializer_class = PostShareSerializer
    permission_classes = (IsAuthenticated, HasAccessToPost,)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = PostShareSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsSuperUser, HasAccessToPost)

    def get(self, request, *args, **kwargs):
        try:
            return Response({'data': self.retrieve(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, *args, **kwargs):
        try:
            return Response({'data': self.update(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        try:
            return Response({'data': self.destroy(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

class PostCommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, HasAccessToPost)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(post=Post.objects.get(id=kwargs['pk']))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = CommentSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsSuperUser, HasAccessToComment)

    def get(self, request, *args, **kwargs):
        try:
            return Response({'data': self.retrieve(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, *args, **kwargs):
        try:
            return Response({'data': self.update(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        try:
            return Response({'data': self.destroy(request, *args, **kwargs).data})
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUser,)

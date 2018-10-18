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
User = get_user_model()

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == get_user(request)

class IsSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        print(get_user(request).is_superuser)
        return get_user(request).is_superuser;

class IsInGroup(permissions.BasePermission):

    def has_permission(self, request, view):
        return get_user(request) in Group.objects.get(id=view.kwargs['pk']).users.all()

class HasAccessToPost(permissions.BasePermission):

    def has_permission(self, request, view):
        #pk = post_id
        return get_user(request) in Post.objects.get(id=view.kwargs["pk"]).group.users.all()

class HasAccessToComment(permissions.BasePermission):

    def has_permission(self, request, view):
        #pk = comment_id
        return get_user(request) in Comment.objects.get(id=view.kwargs["pk"]).post.group.users.all()

class GroupPostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsInGroup,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(group = Group.objects.get(id=kwargs['pk']))
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

class PostLike(generics.ListCreateAPIView):
    queryset = UserLikePost.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = (HasAccessToPost,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        serializer = PostLikeSerializer(queryset, many=True)
        return Response(serializer.data)

class PostFlag(generics.ListCreateAPIView):
    queryset = UserFlagPost.objects.all()
    serializer_class = PostFlagSerializer
    permission_classes = (HasAccessToPost,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        serializer = PostFlagSerializer(queryset, many=True)
        return Response(serializer.data)

class PostShare(generics.ListCreateAPIView):
    queryset = UserSharePost.objects.all()
    serializer_class = PostShareSerializer
    permission_classes = (HasAccessToPost,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
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
        queryset = self.get_queryset().filter(post=Post.objects.get(id=kwargs['pk']))
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

from kidsbook.models import *
from kidsbook.serializers import *
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

#################################################################################################################
## PERMISSIONS ##

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
        return request.user.is_superuser

class IsInGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        # If there are no `pk`
        group_id = view.kwargs.get('group_id', None)
        if group_id:
            #return get_user(request) in Group.objects.get(id=group_id).users.all()
            return Group.objects.get(id=group_id).users.filter(id=request.user.id).exists()
        return False

class HasAccessToPost(permissions.BasePermission):
    def has_permission(self, request, view):
        #pk = post_id
        post_id = view.kwargs.get('post_id', None)
        if post_id:
            #return get_user(request) in Post.objects.get(id=post_id).group.users.all()
            return Post.objects.get(id=post_id).group.users.filter(id=request.user.id).exists()
        return False

class HasAccessToComment(permissions.BasePermission):
    def has_permission(self, request, view):
        #pk = comment_id
        comment_id = view.kwargs.get('comment_id', None)
        if comment_id:
            #return get_user(request) in Comment.objects.get(id=comment_id).post.group.users.all()
            return Comment.objects.get(id=comment_id).post.group.users.filter(id=request.user.id).exists()
        return False

#################################################################################################################

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

class CommentLike(generics.ListCreateAPIView):
    queryset = UserLikeComment.objects.all()
    serializer_class = CommentLikeSerializer
    permission_classes = (HasAccessToComment,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(comment = Comment.objects.get(id=kwargs['comment_id']))
        serializer = CommentLikeSerializer(queryset, many=True)
        return Response(serializer.data)

class PostFlag(generics.ListCreateAPIView):
    queryset = UserFlagPost.objects.all()
    serializer_class = PostFlagSerializer
    permission_classes = (HasAccessToPost,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['post_id']))
        serializer = PostFlagSerializer(queryset, many=True)
        return Response(serializer.data)

class CommentFlag(generics.ListCreateAPIView):
    queryset = UserFlagComment.objects.all()
    serializer_class = CommentFlagSerializer
    permission_classes = (HasAccessToComment,) #Is in group

    def list(self, request, **kwargs):
        queryset = self.get_queryset().filter(comment = Comment.objects.get(id=kwargs['comment_id']))
        serializer = CommentFlagSerializer(queryset, many=True)
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

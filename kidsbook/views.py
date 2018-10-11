from kidsbook.models import Post, Comment
from kidsbook.serializers import CensoredPostSerializer, ActualPostSerializer, CommentSerializer, UserSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from rest_framework import permissions
from profanity import profanity

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
        return obj.owner == request.user

class IsSuperUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser;

class CensoredPostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = CensoredPostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = CensoredPostSerializer(queryset, many=True)
        for post in serializer.data:
            post['content'] = profanity.censor(post['content'])
        return Response(serializer.data)

class ActualPostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = ActualPostSerializer
    permission_classes = (IsSuperUser,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user) 

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = ActualPostSerializer
    permission_classes = (IsSuperUser,)

class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsSuperUser,)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUser,)



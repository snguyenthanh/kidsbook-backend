from rest_framework import permissions, status
from kidsbook.models import *
from kidsbook.serializers import *
from rest_framework.response import Response
class IsTokenValid(permissions.BasePermission):
    def has_permission(self, request, view):
        user_id = request.user.id            
        is_allowed_user = True
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            is_blackListed = BlackListedToken.objects.get(user=user_id, token=token)
            if is_blackListed:
                is_allowed_user = False
        except BlackListedToken.DoesNotExist:
            is_allowed_user = True
        return is_allowed_user

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
        group_id = view.kwargs.get('pk', None)
        if group_id:
            try:
                return Group.objects.get(id=group_id).users.filter(id=request.user.id).exists()
            except Exception:
                pass
        return False

class HasAccessToPost(permissions.BasePermission):
    def has_permission(self, request, view):
        #pk = post_id
        post_id = view.kwargs.get('pk', None)
        if post_id:
            #return get_user(request) in Post.objects.get(id=post_id).group.users.all()
            return Post.objects.get(id=post_id).group.users.filter(id=request.user.id).exists()
        return False

class HasAccessToComment(permissions.BasePermission):
    def has_permission(self, request, view):
        #pk = comment_id
        comment_id = view.kwargs.get('pk', None)
        if comment_id:
            #return get_user(request) in Comment.objects.get(id=comment_id).post.group.users.all()
            return Comment.objects.get(id=comment_id).post.group.users.filter(id=request.user.id).exists()
        return False

class IsGroupCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        group_id = view.kwargs.get('pk', None)
        #sender_id = request.data.get('sender_id', None)
        sender_id = request.user.id

        # If sender is not the Creator of group
        if not sender_id or str(sender_id) != str(Group.objects.get(id=group_id).creator.id):
            return False
        return True

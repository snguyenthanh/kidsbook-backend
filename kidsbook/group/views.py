from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework import status
from uuid import UUID

#from kidsbook.group.serializers import GroupSerializer
from kidsbook.serializers import UserSerializer, GroupSerializer
from kidsbook.models import Group, GroupMember

User = get_user_model()

#################################################################################################################
## PERMISSIONS ##

class IsGroupCreator(BasePermission):
    def has_permission(self, request, view):
        group_id = view.kwargs.get('group_id', None)
        #sender_id = request.data.get('sender_id', None)
        sender_id = request.user.id

        # If sender is not the Creator of group
        if not sender_id or str(sender_id) != str(Group.objects.get(id=group_id).creator.id):
            return False
        return True


#################################################################################################################
## GROUP ##

def get_user_id_from_request_data(request_data: dict):
    uuid = request_data.pop('creator', None)

    if isinstance(uuid, list) and len(uuid) == 1:
        return uuid[0]
    return uuid

def get_groups(request):
    """Return all created groups."""

    try:
        groups = Group.objects.all()
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)

    
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)

def create_group(request):
    # Make a copy of data, as it is immutable
    request_data = request.data.copy()

    try:
        creator = request.user
    except Exception:
        return Response('Bad request.', status=status.HTTP_400_BAD_REQUEST)

    serializer = GroupSerializer(data=request_data)

    # Use `id` as `is_valid()` requires an UUID
    request_data['creator'] = creator.id
    if serializer.is_valid():
        try:
            # Re-assign the `User` object
            request_data['creator'] = creator
            new_group = Group.objects.create_group(**request_data)
            return Response({'result': 'Successful', 'created_group_id': new_group.id}, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({'result': 'Unsuccessful', 'error': exc}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def group(request):
    """Return all groups or create a new group."""

    function_mappings = {
        'GET': get_groups,
        'POST': create_group
    }
    if request.method in function_mappings:
        return function_mappings[request.method](request)
    return Response('Bad request.', status=status.HTTP_400_BAD_REQUEST)


#################################################################################################################
## GROUP MEMBER ##

def add_member_to_group(user, group):
    group.add_member(user)

def delete_member_from_group(user, group):
    # Remove the link between the user and group
    if user.id == group.creator.id:
        raise ValueError('Cannot delete the Creator from the group.')

    GroupMember.objects.get(user_id=user.id, group_id=group.id).delete()

@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, IsGroupCreator))
def group_member(request, **kargs):
    """Add new member or remove a member in a group."""

    function_mappings = {
        'POST': add_member_to_group,
        'DELETE': delete_member_from_group
    }

    try:
        group_id = kargs.get('group_id', None)
        user_id = kargs.get('user_id', None)
        if group_id and user_id:
            new_member = User.objects.get(id=user_id)
            target_group = Group.objects.get(id=group_id)

            # Both POST and DELETE requests require getting group_id and user_id
            function_mappings[request.method](new_member, target_group)

            return Response({'result': 'Successful'}, status=status.HTTP_202_ACCEPTED)
    except Exception:
        pass

    return Response('Bad request.', status=status.HTTP_400_BAD_REQUEST)


#################################################################################################################
## GROUP MANAGE ##

@api_view(['DELETE'])
@permission_classes((IsAuthenticated, IsGroupCreator))
def delete_group(request, **kargs):
    """Delete a group."""

    try:
        group_id = kargs.get('group_id', None)
        if group_id:
            target_group = Group.objects.get(id=group_id)

            # The relations in GroupMember table are also auto-removed
            target_group.delete()
            return Response({'result': 'Successful'}, status=status.HTTP_202_ACCEPTED)
    except Exception:
        pass

    return Response('Bad request.', status=status.HTTP_400_BAD_REQUEST)

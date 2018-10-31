from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework import status, generics
from uuid import UUID
from itertools import chain

#from kidsbook.group.serializers import GroupSerializer
from kidsbook.serializers import *
from kidsbook.models import *
from kidsbook.permissions import *
from kidsbook.utils import *

User = get_user_model()

## GROUP ##

def get_users_not_in_groups(request):
    """Return all created groups."""

    try:
        all_users = iter(User.objects.all())
        users_not_in_any_groups = list(filter(
            lambda user: not GroupMember.objects.filter(user_id=user.id).exists(), all_users
        ))
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(users_not_in_any_groups, many=True)
    return Response({'data': serializer.data})

@api_view(['GET'])
@permission_classes((IsAuthenticated, IsTokenValid, IsSuperUser))
def non_group(request):
    """Return users who are not in any groups."""

    function_mappings = {
        'GET': get_users_not_in_groups
    }
    if request.method in function_mappings:
        return function_mappings[request.method](request)
    return Response({'error': 'Bad request.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsTokenValid, IsSuperUser))
def users_allowed_to_be_discovered(request):
    """Return all superusers, all users in the same group or have no groups or created by the requester."""

    try:
        # USERS HAVE NO GROUPS
        all_users = iter(User.objects.all())
        users_not_in_any_groups = list(filter(
            lambda user: not GroupMember.objects.filter(user_id=user.id).exists(), all_users
        ))

        # ALL SUPER USERS
        all_superusers = User.objects.filter(role=1).exclude(id=request.user.id)

        # ALL USERS IN SAME GROUPS
        group_ids = GroupMember.objects.filter(user_id=request.user.id).distinct().values_list('group_id', flat=True)
        user_ids_in_same_groups = GroupMember.objects.filter(group_id__in=group_ids).distinct().values_list('user_id', flat=True)
        all_users_in_same_groups = User.objects.filter(id__in=user_ids_in_same_groups).distinct().exclude(id=request.user.id)

        # CREATED BY REQUESTER
        users_created_by_requester = User.objects.filter(teacher=request.user)

        # Merge and serializer
        result_list = list(set(chain(users_not_in_any_groups, all_superusers, all_users_in_same_groups, users_created_by_requester)))
        result_list = sorted(result_list, key=lambda instance: instance.created_at, reverse=True)
        serializer = UserSerializer(result_list, many=True)

        if('num_days' in request.data):
            num_days = request.data['num_days']
        else:
            num_days = 0
        for user in serializer.data:
            user['time_history'] = usage_time(User.objects.get(id=user['id']), num_days)

        return Response({'data': serializer.data})
    except Exception as exc:
        Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)

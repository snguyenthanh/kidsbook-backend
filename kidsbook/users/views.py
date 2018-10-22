from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework import status, generics
from uuid import UUID

#from kidsbook.group.serializers import GroupSerializer
from kidsbook.serializers import *
from kidsbook.models import *
from kidsbook.permissions import *

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

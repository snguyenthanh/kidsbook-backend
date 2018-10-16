from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from uuid import UUID
from django.contrib.auth import get_user_model

from kidsbook.group.serializers import GroupSerializer
from kidsbook.models import Group

User = get_user_model()

def get_user_id_from_request_data(request_data: dict):
    uuid = request_data.pop('creator', None)

    if isinstance(uuid, list) and len(uuid) == 1:
        return uuid[0]

    return uuid


@api_view(['GET', 'POST'])
def get_groups(request):
    """Return all roups or insert a new post."""

    if request.method == 'GET':
        try:
            groups = Group.objects.all()
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Make a copy of data, as it is immutable
        request_data = request.data.copy()

        try:
            user_id = UUID(get_user_id_from_request_data(request_data))
            creator = User.objects.get(id=user_id)
        except Exception:
            return Response('Bad authentication.', status=status.HTTP_400_BAD_REQUEST)

        serializer = GroupSerializer(data=request_data)

        # Use `id` as `is_valid()` requires an UUID
        request_data['creator'] = creator.id
        if serializer.is_valid():
            # Re-assign the `User` object
            creator.__class__ = User
            request_data['creator'] = creator
            Group.objects.create_group(**request_data)
            return Response({'result': 'Successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

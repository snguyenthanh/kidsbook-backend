import os
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.parsers import FileUploadParser
from rest_framework import status
from pprint import pprint
from csv import reader
from typing import List

#from kidsbook.group.serializers import GroupSerializer
from kidsbook.serializers import UserSerializer, GroupSerializer
from kidsbook.models import Group, GroupMember
from kidsbook.permissions import IsSuperUser
User = get_user_model()

def read_file_obj_to_list(file_obj) -> List[str]:
    # Remove the wrapper of the request
    data = file_obj.readlines()
    header_index = 0
    for index, row in iter(enumerate(data)):
        row = str(row)
        if 'username' in row and 'password' in row and 'email_address' in row:
            header_index = index
            break
    data = data[header_index:-2]

    # Convert bytes to str in `utf-8`
    data = [row.decode('utf-8') for row in iter(data)]

    # Read the strings using csv.reader
    csv_reader = list(reader(data))
    headers, data = csv_reader[0], csv_reader[1:]
    return list(csv_reader)[1:], csv_reader[0]

def create_user_from_list(arr: List[str], mappings: dict):# Careful with the indices of the input list
    user = {
        key: arr[val]
        for key, val in iter(mappings.items())
        if val < len(arr)
    }

    user['gender'] = int(user.get('gender', 0)) > 0
    user['is_superuser'] = int(user.get('gender', 0)) > 0

    # Create the user/superuser
    if user.get('is_superuser', False):
        User.objects.create_superuser(**user)
    else:
        User.objects.create_user(**user)


#################################################################################################################
## BATCH CREATE ##

@api_view(['POST'])
@permission_classes((IsAuthenticated, IsSuperUser))
@parser_classes((FileUploadParser,))
def batch_create(request, **kargs):
    file_obj = request.data.get('file', None)

    if not file_obj:
        return Response('Bad request.', status=status.HTTP_400_BAD_REQUEST)

    user_list, headers = read_file_obj_to_list(file_obj)
    mapping_fields = {
        field: index
        for index, field in iter(enumerate(headers))
    }

    failed_users = []
    for user in iter(user_list):
        try:
            create_user_from_list(user, mapping_fields)
        except Exception:
            failed_users.append(user)

    if failed_users:
        return Response({
            'result': 'Unsuccessful',
            'error': 'Unable to read {} users'.format(len(failed_users)),
            'data': failed_users
        }, status=status.HTTP_409_CONFLICT)

    return Response({'result': 'Successful'}, status=status.HTTP_202_ACCEPTED)
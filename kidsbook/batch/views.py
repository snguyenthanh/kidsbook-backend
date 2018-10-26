from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.parsers import FileUploadParser
from csv import reader
from typing import List
from django.db import Error, transaction

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

    # Convert bytes to str in `utf-8`
    data = [row.decode('utf-8') for row in iter(data)]

    # To get the last index, count if it has the same number of commas as the header
    number_of_commas = data[header_index].count(',')
    last_index = header_index
    for index in iter(range(len(data)-1, -1, -1)):
        if data[index].count(',') == number_of_commas:
            last_index = index
            break

    data = data[header_index:last_index+1]
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
    if user.get('is_superuser', '0') != '0':
        raise TypeError('Only Admin-level users can create superusers.')
    if 'role' in user and user['role'] <= 1:
        raise TypeError('Only Admin-level users can create superusers.')

    user = {k: v for k, v in user.items() if str(v) != ''}

    # Create the user/superuser
    if user.get('is_superuser', False):
        created_user = User.objects.create_superuser(**user)
    else:
        created_user = User.objects.create_user(**user)
    return str(created_user.id)


#################################################################################################################
## BATCH CREATE ##

@api_view(['POST'])
@permission_classes((IsAuthenticated, IsSuperUser))
@parser_classes((FileUploadParser,))
def batch_create(request, filename, format=None):
    file_obj = request.data.get('file', None)

    if not file_obj:
        return Response('Bad request.', status=status.HTTP_400_BAD_REQUEST)

    user_list, headers = read_file_obj_to_list(file_obj)
    mapping_fields = {
        field: index
        for index, field in iter(enumerate(headers))
    }

    created_users = []
    error = None
    try:
        with transaction.atomic():
            for user in iter(user_list):
                created_users.append(
                    create_user_from_list(user, mapping_fields)
                )
    except Error as db_err:
        error = str(db_err)
    except Exception as exc:
        error = str(exc)

    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'data': {'created_users': created_users}}, status=status.HTTP_202_ACCEPTED)

from django.shortcuts import render
from kidsbook.models import *
from kidsbook.serializers import *
from kidsbook.permissions import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
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
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model, get_user, authenticate
import jwt, json, ujson
from rest_framework_jwt.utils import jwt_payload_handler
from django.contrib.auth.signals import user_logged_in
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny
# import settings
permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

SECRET_KEY = 'a5)t3&0wu-u*8ti(ru_b72vmz8d3pliuuqh8b7i_t^e(aci-1l'

def generate_token(user):
    payload = jwt_payload_handler(user)
    return jwt.encode(payload, SECRET_KEY)

class LogIn(APIView):
    permission_classes = (AllowAny, )
    def post(self, request):
        # print("SECRET")
        # print(settings.SECRET_KEY)
        try:
            email = request.data['email_address']
            user = User.objects.get(email_address=email)
            if(user.check_password(request.data['password']) == False):
                raise ValueError('Wrong email/password')
            if user:
                try:
                    token = generate_token(user)
                    user_details = {}
                    user_details['name'] = user.username
                    user_details['token'] = token
                    user_logged_in.send(sender=user.__class__,
                                        request=request, user=user)
                    return Response({'data': user_details}, status=status.HTTP_200_OK)

                except Exception as e:
                    return Response({'error': e})
            else:
                res = {
                    'error': 'can not authenticate with the given credentials or the account has been deactivated'}
                return Response({'error': res}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)})

class Register(APIView):
    # permission_classes = (IsSuperUser, IsInGroup)
    serializer_class = UserSerializer
    def post(self, request):
        user_role = request.data['type']
        group = Group.objects.get(id=request.data['group_id'])
        if(user_role == 'ADMIN' or user_role == 'SUPERUSER'):
            user = User.objects.create_superuser(
                email_address=request.data['email_address'],
                realname=request.data['realname'],
                username=request.data['username'],
                password=request.data['password']
            )
        elif(user_role == 'USER'):
            user = User.objects.create_user(
                email_address=request.data['email_address'],
                realname=request.data['realname'],
                username=request.data['username'],
                password=request.data['password'],
            )
        elif(user_role == 'VIRTUAL_USER'):
            user = User.objects.create_virtual_user(
                email_address=request.data['email_address'],
                realname=request.data['realname'],
                password=request.data['password'],
                username=request.data['username'],
                teacher=request.user,
            )
        group.add_member(user)
        serializer = self.serializer_class(user, many=False)
        return Response({'data': serializer.data})


class Update(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        current_user = request.user
        serializerOld = self.serializer_class(current_user, many=False)

        request_data = serializerOld.data.copy()

        if(request.user.is_superuser):
            request_data['displayname'] = request.data['new_displayname']

        request_data['username'] = request.data['new_username']

        serializerNew = self.serializer_class(current_user, data=request_data)
        if(serializerNew.is_valid()):
            print("A HERE")
            serializerNew.save()
            # print(request.data['new_user_name'])

        return Response(serializerNew.data)
        # User.objects.update_user(current_user)
        # serializer = UserSerializer(current_user,)

class GetInfo(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    def list(self, request):
        try:
            current_user = request.user
            serializer = self.serializer_class(current_user, many=False)
            return Response({'data': serializer.data})
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

# class GetGroup(generics.ListAPIView):
#     serializer_class = GroupSerializer
#     permission_classes = (IsSuperUser,)
#     def list(self, request):
#         groups = Group.objects.


class GetInfoUser(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    def list(self, request, **kargs):
        try:
            user_id = kargs.get('user_id', None)
            if user_id:
                user = User.objects.get(id=user_id)
                if(request.user.is_superuser):
                    self.serializer_class = UserSerializer
                else:
                    self.serializer_class = UserPublicSerializer
                serializer = self.serializer_class(user, many=False)
                return Response({'data': serializer.data})
        except Exception:
            pass

        return Response({'error' : 'Bad request.'}, status=status.HTTP_400_BAD_REQUEST)

class GetPost(generics.ListAPIView):
    queryset = ''
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    def list(self, request):
        try:
            current_user = request.user
            posts = Post.objects.filter(creator=current_user)
            serializer = PostSerializer(posts, many=True)
            return Response({'data': serializer.data})
        except Exception as e:
            return Response({'error': e})

class GetVirtualUser(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsSuperUser,)
    def list(self, request):
        try:
            current_user = request.user
            virtual_users = User.objects.filter(teacher=current_user)
            serializer = self.serializer_class(virtual_users, many=True)
            return Response({'data': serializer.data})
        except Exception as e: 
            return Response({'error': e})
# Create your views here.

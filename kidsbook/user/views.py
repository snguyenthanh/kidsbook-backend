from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework import permissions
from profanity import profanity

from django.http import (
    HttpResponse, HttpResponseNotFound, JsonResponse
)
from django.contrib.auth import (
    authenticate, login, logout
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model, authenticate
import jwt, json, ujson
from rest_framework_jwt.utils import jwt_payload_handler
from django.contrib.auth.signals import user_logged_in
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny

from kidsbook.models import *
from kidsbook.serializers import *
from kidsbook.permissions import *


# import settings
permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

SECRET_KEY = 'a5)t3&0wu-u*8ti(ru_b72vmz8d3pliuuqh8b7i_t^e(aci-1l'

def generate_token(user):
    payload = jwt_payload_handler(user)
    return jwt.encode(payload, SECRET_KEY)

class LogIn(APIView):
    permission_classes = (AllowAny, )
    def post(self, request):
        email = request.data.get('email_address', None)
        password = request.data.get('password', None)
        if not email or not password:
            res = {'error': 'please provide a email and a password'}
            return Response({'error': res}, status=status.HTTP_403_FORBIDDEN)

        isAuthenticate = authenticate(email_address=email, password=password)
        if(isAuthenticate is None):
            res = {'error': ' Wrong email/password'}
            return Response({'error': res}, status=status.HTTP_403_FORBIDDEN)
        user = User.objects.get(email_address=email)
        try:
            token = generate_token(user)
            user_details = {}
            user_details['name'] = user.username
            user_details['token'] = token
            user_logged_in.send(sender=user.__class__,
                                request=request, user=user)
            return Response({'data': user_details}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        res = {'error': 'can not authenticate with the given credentials or the account has been deactivated'}
        return Response({'error': res}, status=status.HTTP_400_BAD_REQUEST)

class LogInAsVirtual(APIView):
    permission_classes = (IsAuthenticated, IsSuperUser, IsTokenValid)

    def post(self, request):
        email = request.data.get('email_address', None)

        # Check if eligible
        if not email or not User.objects.filter(email_address=email).exists():
            return Response({'error': 'The email is invalid.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        user = User.objects.get(email_address=email)
        if not user.teacher or user.teacher.id != request.user.id:
            return Response({'error': "The user doesn't have permission to access this user."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            token = generate_token(user)
            user_details = {}
            user_details['name'] = user.username
            user_details['token'] = token
            user_logged_in.send(sender=user.__class__,
                                    request=request, user=user)
            return Response({'data': user_details}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class Register(APIView):
    permission_classes = (IsAuthenticated, IsSuperUser, IsTokenValid)
    serializer_class = UserSerializer

    def post(self, request):
        # Make a copy of data, as it is immutable
        request_data = request.data.dict().copy()

        user_role = request_data.pop('type', 'USER')
        teacher = request_data.pop('teacher', None)

        mapping_create = {
            'ADMIN': User.objects.create_superuser,
            'SUPERUSER': User.objects.create_superuser,
            'USER': User.objects.create_user,
            'VIRTUAL_USER': User.objects.create_virtual_user
        }

        if user_role in ('USER', 'VIRTUAL_USER') and not teacher:
            return Response({'error': "A creator's ID is required."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if teacher:
            try:
                teacher = User.objects.get(id=teacher)
                if teacher.is_superuser:
                    request_data['teacher'] = teacher
                else:
                    return Response({'error': "The teacher is not a superuser"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except Exception:
                return Response({'error': "Invalid teacher's ID."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        user = mapping_create[user_role](**request_data)

        # group = Group.objects.get(id=request.data['group_id'])
        # group.add_member(user)
        serializer = self.serializer_class(user)
        return Response({'data': serializer.data}, status=status.HTTP_202_ACCEPTED)


class Update(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)

    def post(self, request, **kargs):
        target_user_id = kargs['pk']
        if not User.objects.filter(id=target_user_id).exists():
            return Response({'error': 'User not found.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        # Check for permission
        keywords_require_superuser = ('email_address', 'username', 'realname')
        if any(kw in kargs for kw in iter(keywords_require_superuser)) and not request.user.is_superuser:
            return Response({'error': 'Only superuser and above of this user can edit email, username and real name.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if request.user.id != User.objects.get(id=target_user_id).teacher.id and request.user.id != target_user_id:
            return Response({'error': 'Only the creator and this user can edit.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        allowed_keywords = ['gender', 'description', 'date_of_birth', 'avatar_url']
        # If differnt user_id, the requester must be the creator
        if request.user.id != target_user_id:
            allowed_keywords = set(allowed_keywords + list(keywords_require_superuser))

        # Update the user
        target_user = User.objects.get(id=target_user_id)
        update_data = {
            key: val
            for key, val in iter(request.data.items())
            if key in allowed_keywords
        }

        for attr, value in update_data.items():
            setattr(target_user, attr, value)

        if 'password' in request.data:
            target_user.set_password(request.data['password'])

        try:
            target_user.save()
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        serializers = UserSerializer(target_user)
        return Response({'data': serializers.data}, status=status.HTTP_202_ACCEPTED)

class GetGroups(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)

    def list(self, request, **kwargs):
        user_id = kwargs['pk']

        if not User.objects.filter(id=user_id).exists():
            return Response({'error': 'The user doesnt exist.'}, status=status.HTTP_400_BAD_REQUEST)

        group_members = GroupMember.objects.filter(user=user_id)
        group_infos = [
            Group.objects.get(id=group_member.group_id) for group_member in iter(group_members)
        ]

        serializer = GroupSerializer(group_infos, many=True)
        return Response({'data': serializer.data})

class LogOut(generics.ListAPIView):
    permission_class = (IsAuthenticated, IsTokenValid)
    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            BlackListedToken.objects.create(token=token, user=request.user)
            return Response({}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetInfoUser(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsTokenValid)
    def list(self, request, **kargs):
        try:
            user_id = kargs.get('pk', None)
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
    permission_classes = (IsAuthenticated, IsTokenValid)
    def list(self, request):
        try:
            current_user = request.user
            posts = Post.objects.filter(creator=current_user).order_by('-created_at')
            serializer = PostSerializer(posts, many=True)
            return Response({'data': serializer.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetVirtualUsers(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsSuperUser, IsTokenValid)
    def list(self, request):
        try:
            current_user = request.user
            virtual_users = User.objects.filter(teacher=current_user, role=3)
            serializer = self.serializer_class(virtual_users, many=True)
            return Response({'data': serializer.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

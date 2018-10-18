from django.shortcuts import render
from kidsbook.models import *
from kidsbook.serializers import *
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

class LogIn(APIView):
    permission_classes = (AllowAny, )
    def post(self, request):
        # print("SECRET")
        # print(settings.SECRET_KEY)
        try:
            email = request.data['email_address']
            #password = request.data['password']
            #user = authenticate(username='hieu2', password=password)
            #print(user)
            user = User.objects.get(email_address=email)
            print("CHECK")
            #print(user.check_password(password))
            if user:
                try:
                    payload = jwt_payload_handler(user)

                    token = jwt.encode(payload, SECRET_KEY)
                    user_details = {}
                    user_details['name'] = user.username
                    user_details['token'] = token
                    user_logged_in.send(sender=user.__class__,
                                        request=request, user=user)
                    return Response(user_details, status=status.HTTP_200_OK)

                except Exception as e:
                    raise e
            else:
                res = {
                    'error': 'can not authenticate with the given credentials or the account has been deactivated'}
                return Response(res, status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            res = {'error': 'please provide a email and a password'}
            return Response(res)

class Register(APIView):
    permission_classes = (AllowAny, )
    serializer_class = UserSerializer
    def post(self, request):
        user = User.objects.create_superuser(
            email_address=request.data['email_address'],
            username=request.data['username'],
            password=request.data['password'],
            role=1,
        )
        serializer = self.serializer_class(user, many=False)
        return Response(serializer.data)


class Update(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        current_user = request.user
        serializerOld = self.serializer_class(current_user, many=False)

        request_data = serializerOld.data.copy()
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
        current_user = request.user
        serializer = self.serializer_class(current_user, many=False)
        return Response(serializer.data)

class GetPost(generics.ListAPIView):
    queryset = ''
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    def list(self, request):
        current_user = request.user
        posts = Post.objects.filter(creator=current_user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

# Create your views here.

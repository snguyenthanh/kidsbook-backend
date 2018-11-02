import copy
from kidsbook.models import *
from kidsbook.serializers import *
from kidsbook.permissions import *
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated

from django.http import (
    HttpResponse, HttpResponseNotFound, JsonResponse
)
from django.contrib.auth import (
    authenticate, login, logout
)
from django.db.models import Case, Count, IntegerField, Sum, When, F

from django.contrib.auth import get_user_model, get_user
from rest_framework.permissions import IsAuthenticated, AllowAny
from kidsbook.utils import *
from django.db import connection, reset_queries
from pprint import pprint



User = get_user_model()

class GroupPostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated, IsTokenValid, IsInGroup)

    def get_serializer_class(self):
        if self.request.user.role.id <= 1:
            return PostSuperuserSerializer
        else:
            return PostSerializer

    def list(self, request, **kwargs):
        print(len(connection.queries))

        try:
            # Get all posts in the group
            user_role_id = request.user.role.id
            post_queryset = Post.objects.filter(group__id = kwargs['pk'])

            if ('all' in request.query_params
                    and str(request.query_params.get('all', 'false')).lower() == 'true'
                    and user_role_id <= 1
                    ):
                pass
            else:
                post_queryset = post_queryset.exclude(is_deleted=True)

            post_queryset = post_queryset.order_by('-created_at')
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Change the Serializer depends on the role of requester
        if user_role_id <= 1:
            post_queryset = PostSuperuserSerializer.setup_eager_loading(post_queryset)
            serializer = PostSuperuserSerializer(post_queryset, many=True)
        else:
            post_queryset = PostSerializer.setup_eager_loading(post_queryset)
            serializer = PostSerializer(post_queryset, many=True)

        reset_queries()
        response_data = serializer.data
        print(len(connection.queries))

        reset_queries()
        comment_queryset = Comment.objects.filter(post__in=post_queryset).exclude(is_deleted=True)
        comment_queryset.query.group_by = ['id']
        comment_queryset = comment_queryset.annotate(
            like_count=Count('likes')
        ).order_by('-like_count', '-created_at')[:3]

        comment_queryset = CommentSerializer.setup_eager_loading(comment_queryset)
        comments_serializer_data = CommentSerializer(comment_queryset, many=True).data
        print(len(connection.queries))

        reset_queries()
        likes_queryset = UserLikePost.objects.filter(post__in=post_queryset).exclude(like_or_dislike=False)
        likes_queryset = PostLikeSerializer.setup_eager_loading(likes_queryset)
        likes_queryset_data = PostLikeSerializer(likes_queryset, many=True).data

        print(len(connection.queries))

        for post in iter(response_data):
            post['likes_list'] = list(filter(lambda like: like['post']['id'] == post['id'], likes_queryset_data))

            comments_data = list(filter(lambda comment: comment['post']['id'] == post['id'], copy.deepcopy(comments_serializer_data)))[:3]
            for comment in comments_data:
                comment['creator'] = {'id':comment['creator']['id'], 'username': comment['creator']['username']}
            comment_data = clean_data_iterative(comments_data, 'post')
            post['comments'] = comments_data
            post['comments'] = clean_data_iterative(post['comments'], 'likes')

        return Response({'data': response_data})

    def post(self, request, *args, **kwargs):
        return Response({'data': self.create(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        # try:
        #     return Response({'data': self.create(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        # except Exception as exc:
        #     return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class GroupFlaggedList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsInGroup, IsTokenValid, IsSuperUser)

    def list(self, request, **kwargs):
        try:
#             queryset = self.get_queryset().filter(group = Group.objects.get(id=kwargs['pk'])).exclude(flags=[]).order_by('-created_at')
#         except Exception:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(data=queryset, many=True)
            serializer.is_valid()
#         return Response({'data': serializer.data})
            queryset = Post.objects.filter(group = Group.objects.get(id=kwargs['pk'])).exclude(flags__isnull = True)
            post_queryset = UserFlagPost.objects.filter(post__in=queryset).order_by('-created_at')

            # all_posts = Post.objects.all().filter(group = Group.objects.get(id=kwargs['pk']))
            # queryset = Comment.objects.all().filter(post__in = all_posts).exclude(flags__isnull = True)
            # comment_queryset = UserFlagPost.objects.all().filter(comment__in=queryset).order_by('-created_at')

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response_data = PostFlagSerializer(post_queryset, many=True).data
        post_data = []
        comment_data = []

        for flag in response_data:
            flag['user_id'] = flag['user']['id']
            flag['user_photo'] = flag['user']['profile_photo']
            flag['user_name'] = flag['user']['username']
            flag.pop('user', None)
            if(flag['comment'] == None):
                flag.pop('comment', None)
                post_data.append(flag)
            else:
                comment_data.append(flag)

        return Response({'data': {'posts': post_data, 'comments': comment_data}})

class PostLike(generics.ListCreateAPIView):
    queryset = UserLikePost.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, HasAccessToPost,)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk'])).filter(like_or_dislike=True)
        except Exception  as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class CommentLike(generics.ListCreateAPIView):
    queryset = UserLikeComment.objects.all()
    serializer_class = CommentLikeSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, HasAccessToComment)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(comment = Comment.objects.get(id=kwargs['pk']))
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class PostFlag(generics.ListCreateAPIView):
    queryset = UserFlagPost.objects.all()
    serializer_class = PostFlagSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, HasAccessToPost)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        except Exception  as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class CommentFlag(generics.ListCreateAPIView):
    queryset = UserFlagPost.objects.all()
    serializer_class = CommentFlagSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, HasAccessToComment)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(comment = Comment.objects.get(id=kwargs['pk']))
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class PostShare(generics.ListCreateAPIView):
    queryset = UserSharePost.objects.all()
    serializer_class = PostShareSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, HasAccessToPost,)

    def list(self, request, **kwargs):
        try:
            queryset = self.get_queryset().filter(post = Post.objects.get(id=kwargs['pk']))
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, HasAccessToPost)

    def get(self, request, *args, **kwargs):
        post_id = kwargs.get('pk', None)

        if post_id and not Post.objects.filter(id=post_id).exists():
            return Response({'error': 'Post not found'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            post = Post.objects.get(id=post_id)
            if post.is_deleted and not request.user.is_superuser:
                return Response({'error': 'Post not found'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            serializer = PostSerializer(post)
            return Response({'data': serializer.data})
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        # for key, value in request.POST.iteritems():
        #     print((key, value))
        update_data = request.data.dict()
        try:
            Post.objects.filter(id=kwargs.get('pk', None)).update(**update_data)
            return Response({'data': PostSerializer(Post.objects.get(id=kwargs.get('pk', None))).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            post_id = kwargs.get('pk', '')
            post_to_delete = Post.objects.get(id=post_id)
            post_to_delete.is_deleted = True
            post_to_delete.save()
            return Response({}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class PostCommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, HasAccessToPost)

    def get_serializer_class(self):
      if self.request.user.role.id <= 1:
          return CommentSuperuserSerializer
      else:
          return CommentSerializer


    def list(self, request, **kwargs):
        try:
            # Get all comments in the post
            queryset = self.get_queryset().filter(post=Post.objects.get(id=kwargs['pk']))
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if ('all' in request.query_params
                    and str(request.query_params.get('all', 'false')).lower() == 'true'
                    and request.user.role.id <= 1
                    ):
                pass
            else:
                queryset = queryset.exclude(is_deleted=True)

            queryset = queryset.order_by('-created_at')
            serializer = self.get_serializer(data=queryset, many=True)
            serializer.is_valid()
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        for comment in serializer.data:
            comment['like_count'] = len(comment['likes'])
            comment['likers'] = [x['id'] for x in comment['likes']]
        response_data = clean_data_iterative(serializer.data, 'likes')
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, HasAccessToComment)

    def get(self, request, *args, **kwargs):
        comment_id = kwargs.get('pk', None)

        if comment_id and not Comment.objects.filter(id=comment_id).exists():
            return Response({'error': 'Comment not found'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            comment = Comment.objects.get(id=comment_id)
            if comment.is_deleted and not request.user.is_superuser:
                return Response({'error': 'Comment not found'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            serializer = CommentSerializer(comment)
            return Response({'data': serializer.data})
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        update_data = request.data.dict()
        try:
            Comment.objects.filter(id=kwargs.get('pk', None)).update(**update_data)
            return Response({'data': CommentSerializer(Comment.objects.get(id=kwargs.get('pk', None))).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            comment_id = kwargs.get('pk', '')
            comment_to_delete = Comment.objects.get(id=comment_id)
            comment_to_delete.is_deleted = True
            comment_to_delete.save()
            return Response({}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUser,)

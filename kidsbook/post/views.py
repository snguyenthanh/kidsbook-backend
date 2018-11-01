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

User = get_user_model()

class GroupPostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
#     serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsTokenValid, IsInGroup)

    def get_serializer_class(self):
      if self.request.user.role.id <= 1:
          return PostSuperuserSerializer
      else:
          return PostSerializer

    def list(self, request, **kwargs):
        try:
            # Get all posts in the group
            queryset = self.get_queryset().filter(group = Group.objects.get(id=kwargs['pk']))

            if ('all' in request.query_params
                    and str(request.query_params.get('all', 'false')).lower() == 'true'
                    and request.user.role.id <= 1
                    ):
                pass
            else:
                queryset = queryset.exclude(is_deleted=True)

            queryset = queryset.order_by('-created_at')
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        response_data = serializer.data.copy()

        really_likes = UserLikeComment.objects.all().filter(like_or_dislike=True)
        really_likes_users = User.objects.all().filter(id__in=[x.user.id for x in really_likes])

        for post in serializer.data.copy():
            queryset = UserLikePost.objects.all().filter(post=Post.objects.get(id=post['id']))
            likes = PostLikeSerializer(queryset, many=True)
            post['likes_list'] = likes.data.copy()

            queryset = Comment.objects.all().filter(post=Post.objects.get(id=post['id'])).exclude(is_deleted=True)
            queryset.query.group_by = ['id']
            # queryset = queryset.annotate(
            #     like_count=Sum(
            #         Case(
            #             When(likes__in=really_likes_users, then=1),
            #             default=0, output_field=IntegerField()
            #         )
            #     )
            # ).order_by('-like_count', '-created_at')[:3]

            # queryset = queryset.annotate(
            #     like_count=Count(
            #         'likes',
            #         likes__in = User.objects.all().filter(id__in= [x.user.id for x in UserLikeComment.objects.all().filter(comment=Comment.objects.get(id=)).filter(like_or_dislike=True)])
            #     )
            # ).order_by('-like_count', '-created_at')[:3]

            queryset = queryset.annotate(
                like_count=Count('likes')
            ).order_by('-like_count', '-created_at')[:3]

            comments = CommentSerializer(queryset, many=True)
            comments_data = comments.data.copy()
            for comment in comments_data:
                comment['creator'] = {'id':comment['creator']['id'], 'username': comment['creator']['username']}
            comment_data = clean_data_iterative(comments_data, 'post')
            post['comments'] = comments_data.copy()
            post['comments'] = clean_data_iterative(post['comments'], 'likes')
        return Response({'data': serializer.data})

    def post(self, request, *args, **kwargs):
        try:
            return Response({'data': self.create(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class GroupFlaggedList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsInGroup, IsTokenValid, IsSuperUser)

    def list(self, request, **kwargs):
        try:
#             queryset = self.get_queryset().filter(group = Group.objects.get(id=kwargs['pk'])).exclude(flags=[]).order_by('-created_at')
#         except Exception:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         serializer = self.get_serializer(data=queryset, many=True)
#         serializer.is_valid()
#         return Response({'data': serializer.data})
            queryset = Post.objects.all().filter(group = Group.objects.get(id=kwargs['pk'])).exclude(flags__isnull = True)
            post_queryset = UserFlagPost.objects.all().filter(post__in=queryset).order_by('-created_at')

            # all_posts = Post.objects.all().filter(group = Group.objects.get(id=kwargs['pk']))
            # queryset = Comment.objects.all().filter(post__in = all_posts).exclude(flags__isnull = True)
            # comment_queryset = UserFlagPost.objects.all().filter(comment__in=queryset).order_by('-created_at')

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response_data = PostFlagSerializer(post_queryset, many=True).data.copy()
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
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
        update_data = {}
        for tup in request.data.lists():
            update_data[tup[0]] = tup[1][0]
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
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
        update_data = {}
        for tup in request.data.lists():
            update_data[tup[0]] = tup[1][0]
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
            #return Response({'data': self.destroy(request, *args, **kwargs).data}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUser,)

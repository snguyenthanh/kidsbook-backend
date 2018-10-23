from rest_framework import serializers, status
from rest_framework.response import Response
from kidsbook.models import *
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
import opengraph
import json

# This is for private profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email_address', 'is_active', 'is_superuser', 'description', "realname", 'group_users', 'profile_photo')
        depth = 1

# This class is for public profile
class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'is_active', 'is_superuser', 'username', 'description')

class PostSerializer(serializers.ModelSerializer):

    # image = Base64ImageField(
    #     max_length=None, use_url=True,
    # )

    def create(self, data):
        try:
            group = Group.objects.get(id=self.context['view'].kwargs.get("pk"))
        except Exception:
            raise serializers.ValidationError({'error': 'Group Not found'})
        current_user = self.context['request'].user
        # try:
        # print(opengraph.OpenGraph(url=data["link"]).__str__())
        return Post.objects.create(ogp= opengraph.OpenGraph(url=data["link"]).__str__() if 'link' in data else "",
            link=data.get("link", None), picture=data.get("picture", None), content=data["content"], group=group, creator=current_user)
        # except Exception:
            # raise serializers.ValidationError({'error': 'Unknown error while creating post'})

    class Meta:
        model = Post
        fields = ('id', 'created_at', 'content', 'creator', 'group', 'picture', 'link', 'ogp', 'likes', 'flags', 'shares')
        depth = 1

class PostLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLikePost
        fields = ('id', 'user', 'post', 'like_or_dislike')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        new_post, created = UserLikePost.objects.update_or_create(post=post, user=current_user, defaults={'like_or_dislike': data["like_or_dislike"]})
        return new_post

class CommentLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLikeComment
        fields = ('id', 'user', 'comment', 'like_or_dislike')
        depth = 1

    def create(self, data):
        comment = Comment.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        new_comment, created = UserLikeComment.objects.update_or_create(comment=comment, user=current_user, defaults={'like_or_dislike': data["like_or_dislike"]})
        return new_comment

class PostFlagSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFlagPost
        fields = ('id', 'user', 'post', 'status', 'comment')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        new_obj, created = UserFlagPost.objects.update_or_create(post=post, user=current_user, defaults={'status': data["status"], 'comment': None})
        return new_obj

class CommentFlagSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFlagPost
        fields = ('id', 'user', 'post', 'status', 'comment')
        depth = 1

    def create(self, data):
        comment = Comment.objects.get(id=self.context['view'].kwargs.get("pk"))
        post = comment.post
        current_user = self.context['request'].user
        new_obj, created = UserFlagPost.objects.update_or_create(post=post, user=current_user, comment=comment, defaults={'status': data["status"]})
        return new_obj

class PostShareSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSharePost
        fields = ('id', 'user', 'post')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        new_post, created = UserSharePost.objects.get_or_create(post=post, user=current_user)
        return new_post

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'post', 'creator')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        return Comment.objects.create(content=data["content"], post=post, creator=current_user)

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'description', 'creator', 'created_at', 'users')

from rest_framework import serializers, status
from rest_framework.response import Response
from kidsbook.models import *
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
import opengraph
import json
from profanity import profanity
profanity.set_censor_characters("*")

# This is for private profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email_address', 'is_active', 'profile_photo', 'is_superuser', 'description', "realname", 'group_users')
        depth = 1

# This class is for public profile
class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'is_active', 'is_superuser', 'profile_photo', 'username', 'description')


class PostSerializer(serializers.ModelSerializer):

    filtered_content = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    def get_filtered_content(self, obj):
        return profanity.censor(obj.content)

    def get_content(self, obj):
        if(not self.context['request'].user.is_superuser):
            return profanity.censor(obj.content)
        else:
            return obj.content

    def create(self, data):
        try:
            group = Group.objects.get(id=self.context['view'].kwargs.get("pk"))
        except Exception:
            raise serializers.ValidationError({'error': 'Group Not found'})
        current_user = self.context['request'].user
        data = self.context['request'].data
        # try:
        # print(opengraph.OpenGraph(url=data["link"]).__str__())
        return Post.objects.create(ogp= opengraph.OpenGraph(url=data["link"]).__str__() if 'link' in data else "",
            link=data.get("link", None), picture=data.get("picture", None), content=data.get("content", ""), group=group, creator=current_user,
            is_like_enabled = data.get("is_like_enabled", True), is_share_enabled = data.get("is_share_enabled", True), 
            is_flag_enabled = data.get("is_flag_enabled", True), is_comment_enabled = data.get("is_comment_enabled", True))
        # except Exception:
            # raise serializers.ValidationError({'error': 'Unknown error while creating post'})

    class Meta:
        model = Post
        fields = ('id', 'created_at', 'content', 'creator', 'group', 'picture', 'link', 'ogp', 'likes', 'flags', 'shares', 'filtered_content')
        depth = 1

class CommentSerializer(serializers.ModelSerializer):

    filtered_content = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    def get_filtered_content(self, obj):
        return profanity.censor(obj.content)

    def get_content(self, obj):
        if(not self.context['request'].user.is_superuser):
            return profanity.censor(obj.content)
        else:
            return obj.content

    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'post', 'creator', 'filtered_content')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        data = self.context['request'].data
        return Comment.objects.create(content=data["content"], post=post, creator=current_user)

class PostLikeSerializer(serializers.ModelSerializer):

    post = PostSerializer(required=False)

    class Meta:
        model = UserLikePost
        fields = ('id', 'user', 'post', 'like_or_dislike')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        data = self.context['request'].data
        new_post, created = UserLikePost.objects.update_or_create(post=post, user=current_user, defaults={'like_or_dislike': str(data["like_or_dislike"]).strip().lower() == 'true'})
        return new_post

class CommentLikeSerializer(serializers.ModelSerializer):

    comment = CommentSerializer(required=False)

    class Meta:
        model = UserLikeComment
        fields = ('id', 'user', 'comment', 'like_or_dislike')
        depth = 1

    def create(self, data):
        comment = Comment.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        data = self.context['request'].data
        new_comment, created = UserLikeComment.objects.update_or_create(comment=comment, user=current_user, defaults={'like_or_dislike':str(data["like_or_dislike"]).strip().lower() == 'true'})
        return new_comment

class PostFlagSerializer(serializers.ModelSerializer):

    post = PostSerializer(required=False)
    comment = CommentSerializer(required=False)

    class Meta:
        model = UserFlagPost
        fields = ('id', 'user', 'post', 'status', 'comment')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        data = self.context['request'].data
        new_obj, created = UserFlagPost.objects.update_or_create(post=post, user=current_user, defaults={'status': data["status"], 'comment': None})
        return new_obj

class CommentFlagSerializer(serializers.ModelSerializer):

    comment = CommentSerializer(required=False)
    post = PostSerializer(required=False)

    class Meta:
        model = UserFlagPost
        fields = ('id', 'user', 'post', 'status', 'comment')
        depth = 1

    def create(self, data):
        comment = Comment.objects.get(id=self.context['view'].kwargs.get("pk"))
        post = comment.post
        current_user = self.context['request'].user
        data = self.context['request'].data
        new_obj, created = UserFlagPost.objects.update_or_create(post=post, user=current_user, comment=comment, defaults={'status': data["status"]})
        return new_obj

class PostShareSerializer(serializers.ModelSerializer):

    post = PostSerializer(required=False)

    class Meta:
        model = UserSharePost
        fields = ('id', 'user', 'post')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        new_post, created = UserSharePost.objects.get_or_create(post=post, user=current_user)
        return new_post

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'description', 'picture', 'creator', 'created_at', 'users', 'is_like_enabled', 'is_comment_enabled', 'is_share_enabled', 'is_flag_enabled')

class GroupSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSettings
        fields = ('id', 'is_like_enabled', 'is_comment_enabled', 'is_share_enabled', 'is_flag_enabled')

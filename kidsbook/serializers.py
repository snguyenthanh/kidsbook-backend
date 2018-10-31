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
        fields = ('id', 'username', 'email_address', 'is_active', 'profile_photo', 'is_superuser', 'description', "realname", 'group_users', 'user_posts', 'role', 'created_at')
        depth = 1

# This class is for public profile
class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'is_active', 'is_superuser', 'profile_photo', 'username', 'description', 'user_posts')
        depth = 1


class PostSerializer(serializers.ModelSerializer):

    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        return profanity.censor(obj.content)

    def create(self, data):
        try:
            group = Group.objects.get(id=self.context['view'].kwargs.get("pk"))
        except Exception:
            raise serializers.ValidationError({'error': 'Group Not found'})
        current_user = self.context['request'].user
        data = self.context['request'].data
        return Post.objects.create(ogp= opengraph.OpenGraph(url=data["link"]).__str__() if 'link' in data else "",
            link=data.get("link", None), picture=data.get("picture", None), content=data["content"], group=group, creator=current_user)

    class Meta:
        model = Post
        fields = ('id', 'created_at', 'content', 'creator', 'group', 'picture', 'link', 'ogp', 'likes', 'flags', 'shares')
        depth = 1

class CommentSerializer(serializers.ModelSerializer):

    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        return profanity.censor(obj.content)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'post', 'creator')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        data = self.context['request'].data
        return Comment.objects.create(content=data["content"], post=post, creator=current_user)

class PostSuperuserSerializer(serializers.ModelSerializer):

    filtered_content = serializers.SerializerMethodField()

    def get_filtered_content(self, obj):
        return profanity.censor(obj.content)

    def create(self, data):
        try:
            group = Group.objects.get(id=self.context['view'].kwargs.get("pk"))
        except Exception:
            raise serializers.ValidationError({'error': 'Group Not found'})
        current_user = self.context['request'].user
        data = self.context['request'].data
        return Post.objects.create(ogp= opengraph.OpenGraph(url=data["link"]).__str__() if 'link' in data else "",
            link=data.get("link", None), picture=data.get("picture", None), content=data["content"], group=group, creator=current_user)

    class Meta:
        model = Post
        fields = ('id', 'created_at', 'content', 'creator', 'group', 'picture', 'link', 'ogp', 'likes', 'flags', 'shares', 'filtered_content', 'is_deleted')
        depth = 1
        
class CommentSuperuserSerializer(serializers.ModelSerializer):

    filtered_content = serializers.SerializerMethodField()

    def get_filtered_content(self, obj):
        return profanity.censor(obj.content)

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        data = self.context['request'].data
        return Comment.objects.create(content=data["content"], post=post, creator=current_user)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'post', 'creator', 'filtered_content', 'is_deleted')
        depth = 1

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
        new_comment, created = UserLikeComment.objects.update_or_create(comment=comment, user=current_user, defaults={'like_or_dislike': data["like_or_dislike"]})
        if(data["like_or_dislike"] == False):
            old_comment_like = UserLikeComment.objects.get(comment=comment, user=current_user)
            old_comment_like.delete()
        return new_comment

class PostFlagSerializer(serializers.ModelSerializer):

    post = PostSerializer(required=False)
    comment = CommentSerializer(required=False)

    class Meta:
        model = UserFlagPost
        fields = ('id', 'user', 'post', 'status', 'comment', 'created_at')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        data = self.context['request'].data
        new_obj, created = UserFlagPost.objects.update_or_create(post=post, user=current_user, comment__isnull=True, defaults={'status': data["status"], 'comment': None})
        return new_obj

class CommentFlagSerializer(serializers.ModelSerializer):

    comment = CommentSerializer(required=False)
    post = PostSerializer(required=False)

    class Meta:
        model = UserFlagPost
        fields = ('id', 'user', 'post', 'status', 'comment', 'created_at')
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
        fields = ('id', 'name', 'description', 'picture', 'creator', 'created_at', 'users')

class GroupSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSettings
        fields = ('id', 'is_like_enabled', 'is_comment_enabled', 'is_share_enabled', 'is_flag_enabled')

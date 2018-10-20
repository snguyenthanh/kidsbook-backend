from rest_framework import serializers
from kidsbook.models import *
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email_address', 'is_active', 'is_staff', 'description', "realname")

class PostSerializer(serializers.ModelSerializer):

    def create(self, data):
        group = Group.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        return Post.objects.create(content=data["content"], group=group, creator=current_user)

    class Meta:
        model = Post
        fields = ('id', 'created_at', 'content', 'creator', 'group')
        depth = 1

class CompletePostSerializer(serializers.ModelSerializer):

    comments_post = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'created_at', 'content', 'creator', 'group', 'likes', 'shares', 'comments_post')
        depth = 1

class PostLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLikePost
        fields = ('id', 'user', 'post', 'like_or_dislike')
        depth = 1

    def create(self, data):
        post = Post.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        new_post, created = UserLikePost.objects.update_or_create(post=post, user=current_user, defaults={'like_or_dislike': data["like"]})
        return new_post

class CommentLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLikeComment
        fields = ('id', 'user', 'comment', 'like_or_dislike')
        depth = 1

    def create(self, data):
        comment = Comment.objects.get(id=self.context['view'].kwargs.get("pk"))
        current_user = self.context['request'].user
        new_comment, created = UserLikeComment.objects.update_or_create(comment=comment, user=current_user, defaults={'like_or_dislike': data["like"]})
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

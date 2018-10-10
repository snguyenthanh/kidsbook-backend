from rest_framework import serializers
from kidsbook.models import Post, Comment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'posts')

# class PostSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     title = serializers.CharField(required=True, max_length=100)
#     content = serializers.CharField(required=True)

#     def create(self, validated_data):
#         """
#         Create and return a new `Post` instance, given the validated data.
#         """
#         return Post.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         """
#         Update and return an existing `Post` instance, given the validated data.
#         """
#         instance.title = validated_data.get('title', instance.title)
#         instance.content = validated_data.get('content', instance.content)
#         instance.save()
#         return instance

class PostSerializer(serializers.ModelSerializer):
    comments = serializers.PrimaryKeyRelatedField(many=True, queryset=Comment.objects.all())
    post_user = serializers.ReadOnlyField(source='post_user.username')

    class Meta:
        model = Post
        fields = ('id', 'created', 'title', 'content', 'comments', 'post_user')

# class CommentSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     text = serializers.CharField(required=True, max_length=100)
#     post = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

#     def create(self, validated_data):
#         """
#         Create and return a new `Comment` instance, given the validated data.
#         """
#         return Comment.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         """
#         Update and return an existing `Comment` instance, given the validated data.
#         """
#         instance.text = validated_data.get('text', instance.text)
#         instance.save()
#         return instance

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'text', 'post')

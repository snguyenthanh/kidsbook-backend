from rest_framework import serializers
from kidsbook.models import Post, Comment
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email_address', 'is_active', 'is_staff', 'description', "realname")
        # fields = ('email_address',)
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'created_at', 'content', 'creator')
        depth = 1

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
        fields = ('id', 'text', 'post', 'owner')

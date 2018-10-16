from rest_framework import serializers
from kidsbook.models import Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'description', 'creator', 'created_at', 'users')

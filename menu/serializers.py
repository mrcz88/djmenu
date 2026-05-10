from rest_framework import serializers
from .models import Item
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', "email"]

class ItemSerializer(serializers.ModelSerializer):
    #creator = serializers.ReadOnlyField(source='creator.username')
    creator = UserSerializer(read_only=True)
    class Meta:
        model = Item
        fields = ['id', 'item_name', 'item_desc', 'item_price', 'item_image', 'creator']
        read_only_fields = ['creator']


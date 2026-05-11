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

    # Aggiungo field-level validation per il prezzo
    def validate_item_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate(self, attrs):
        if "kebab" in attrs['item_name'].lower():
            raise serializers.ValidationError("Price must be lower than 7")
        if self.instance and self.instance.item_name != attrs['item_name']:
            raise serializers.ValidationError("Item name cannot be changed")
        if self.instance is None:
            Item.objects.filter(item_name__icontains=attrs['item_name'].lower().strip()).exists()
            raise serializers.ValidationError("Item name already exists")
        if self.instance is not None:
            if self.instance.item_name != attrs['item_name']:
                raise serializers.ValidationError("Item name cannot be changed")
        return attrs
        return attrs
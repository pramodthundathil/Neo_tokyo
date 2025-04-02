from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'first_name', 'last_name', 'phone_number','profile_picture',
            'date_of_birth', 'pin_code', 'age', 'district',
            'state', 'address', 'role', 'password'
        ]

    def create(self, validated_data):
        # Use `set_password` to hash the password
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


from .models import DeliveryAddress

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = "__all__"  # Includes all fields
        read_only_fields = ["user"]  # User should be automatically assigned in views

    def create(self, validated_data):
        # Ensure only one primary address per user
        if validated_data.get("is_primary", False):
            DeliveryAddress.objects.filter(user=self.context["request"].user, is_primary=True).update(is_primary=False)
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Ensure only one primary address per user
        if validated_data.get("is_primary", False):
            DeliveryAddress.objects.filter(user=instance.user, is_primary=True).exclude(id=instance.id).update(is_primary=False)
        
        return super().update(instance, validated_data)

from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
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

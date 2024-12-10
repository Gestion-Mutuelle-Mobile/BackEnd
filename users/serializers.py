from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar', None)  # Gestion de l'avatar séparément
        if avatar:
            instance.avatar = avatar
        password = validated_data.pop('password', None)  # Récupérer le mot de passe
        if password:
            instance.set_password(password)  # Chiffrement du mot de passe
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

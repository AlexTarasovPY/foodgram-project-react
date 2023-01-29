
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Subscribe,
    Recipe
)

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор получения данных пользователей модуля djoser.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                Subscribe.objects.filter(subscribed=obj, user=user).exists()
                )


class CustomUserCreateSerializer(UserSerializer):
    """
    Сериализатор создания новых пользователей модуля djoser.
    """

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class RecipeSmallSerializer(serializers.ModelSerializer):
    """
    Сериализатор получения данных пользователей
    для запросов информации о подписках.
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания и удаления подписок пользователя.
    """

    email = serializers.SerializerMethodField()
    id = serializers.PrimaryKeyRelatedField(
        source='subscribed_id', read_only=True
    )
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        if self.context.get('request').query_params.get('recipes_limit'):
            recipes_limit = int(
                self.context.get('request').query_params.get('recipes_limit')
            )
            recipes = Recipe.objects.filter(
                author=obj.subscribed
            )[:recipes_limit]
        else:
            recipes = Recipe.objects.filter(
                author=obj.subscribed
            )
        return RecipeSmallSerializer(recipes, many=True).data

    def get_email(self, obj):
        return obj.subscribed.email

    def get_username(self, obj):
        return obj.subscribed.username

    def get_first_name(self, obj):
        return obj.subscribed.first_name

    def get_last_name(self, obj):
        return obj.subscribed.last_name

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.subscribed).count()

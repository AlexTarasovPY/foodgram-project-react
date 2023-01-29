from rest_framework import serializers

from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from django.db import transaction
from .models import (
    Recipe,
    Ingredient,
    Tag,
    FavoriteRecipes,
    ShoppingList,
    RecipeIngredients,
    Subscribe
)

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для вьюсета ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для вьюсета тэгов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для метода favorite RecipeViewSet.
    Сериализует список рецептов, добавленных пользователями в избранное.
    """
    user = serializers.HiddenField(default='user.id')
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteRecipes
        fields = ('user', 'id', 'name', 'image', 'cooking_time')

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        request = self.context.get('request')
        photo_url = obj.recipe.image.url
        return request.build_absolute_uri(photo_url)

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time

    def validate(self, data):
        try:
            recipe = Recipe.objects.get(id=self.context.get('recipe_id'))
        except Recipe.DoesNotExist:
            raise serializers.ValidationError({
                'errors': 'Рецепт не существует'
            })
        if FavoriteRecipes.objects.filter(
            recipe=recipe, user=self.context['request'].user
        ).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже есть в избранном'
            })
        return data


class ShoppingCartSerializer(FavoriteSerializer):
    """
    Сериалайзер метода shopping_cart вьюсета RecipeViewSet.
    Сериализует список рецептов, добавленных пользователями
    в список для покупок.
    """

    class Meta:
        model = ShoppingList
        fields = ('user', 'id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        try:
            recipe = Recipe.objects.get(id=self.context.get('recipe_id'))

        except Recipe.DoesNotExist:
            raise serializers.ValidationError({
                'errors': 'Рецепт не существует'
            })
        if ShoppingList.objects.filter(
            recipe=recipe, user=self.context['request'].user
        ).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже есть в списке покупок'
            })
        return data


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка ингредиентов, вложенный в RecipeSerializer.
    """

    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = RecipeIngredients
        fields = ('recipe', 'id', 'amount')

    def validate_amount(self, value):
        if value < 1 or value > 32767:
            raise serializers.ValidationError({
                'errors':
                'Количество ингредиента должно быть в интервале 1-32767'})
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор списка рецептов вьюсета RecipeViewSet.
    Используется в методах CREATE, UPDATE, DELETE.
    """

    ingredients = RecipeIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def validate_cooking_time(self, value):
        if value < 1 or value > 32767:
            raise serializers.ValidationError({
                'errors':
                'Время приготовления должно быть в интервале 1-32767'})
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Создание рецепта.
        """

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        create_ingredients = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(create_ingredients)
        return recipe

    def update(self, instance, validated_data):
        """
        Редактирование рецепта.
        """

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()
            create_ingredients = [
                RecipeIngredients(
                    recipe=instance,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
            RecipeIngredients.objects.bulk_create(create_ingredients)
        return super().update(instance, validated_data)

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError({
                'errors': 'Добавьте хотя бы один ингредиент'})
        ingredient_list = []
        for i in (value):
            ingredient_list.append(list(i.values())[0].id)
        ingredient_list_set = set(ingredient_list)
        if len(ingredient_list) != len(ingredient_list_set):
            raise serializers.ValidationError({
                'errors': 'Указанные ингредиенты повторяются'})
        return value

    def validate_tags(self, value):
        if len(value) < 1:
            raise serializers.ValidationError({
                'errors': 'Добавьте хотя бы один тэг'})
        if len(value) != len(set(value)):
            raise serializers.ValidationError({
                'errors': 'Указанные тэги повторяются'})

        return value

    def to_representation(self, obj):
        return RecipeGetSerializer(obj, context=self.context).data


class AuthorRecipeGetSerializer(serializers.ModelSerializer):
    """
    Сераилизатор авторов рецептов, вложенный в RecipeSerializer.
    Используется только для чтения.
    """

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and Subscribe.objects.filter(
                    subscribed=obj, user=user).exists()
                )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )


class IngredientsGetRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов и их количества в рецепте.
    Вложен в сериализатор RecipeGetSerializer.
    Используется для метода GET вьюсета RecipeViewSet.
    """

    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient_id', read_only=True
    )

    def get_name(self, obj):
        return Ingredient.objects.get(id=obj.ingredient_id).name

    def get_measurement_unit(self, obj):
        return Ingredient.objects.get(id=obj.ingredient_id).measurement_unit

    class Meta:
        model = RecipeIngredients
        fields = (
            'id', 'name', 'measurement_unit', 'amount',
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    """
    Сериализатор вьюсета RecipeViewSet для метода GET.
    """

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientsGetRecipeSerializer(
        source='recipeingredients', many=True
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = AuthorRecipeGetSerializer()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and FavoriteRecipes.objects.filter(
            recipe=obj, user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and ShoppingList.objects.filter(
            recipe=obj, user=user).exists())

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

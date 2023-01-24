from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from django.db import transaction
from .models import Recipe, Ingredient, Tag, FavoriteRecipes, ShoppingList
from .models import RecipeIngredients, Subscribe

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class FavoriteSerializer(serializers.ModelSerializer):
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


class ShoppingCartSerializer(FavoriteSerializer):

    class Meta:
        model = ShoppingList
        fields = ('user', 'id', 'name', 'image', 'cooking_time')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = RecipeIngredients
        fields = ('recipe', 'id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    @transaction.atomic
    def create(self, validated_data):
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

    def to_representation(self, obj):
        return RecipeGetSerializer(obj, context=self.context).data


class AuthorRecipeGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscribe.objects.filter(subscribed=obj, user=user).exists()
        else:
            return False

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )


class IngredientsGetRecipeSerializer(serializers.ModelSerializer):
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
        if user.is_authenticated:
            return FavoriteRecipes.objects.filter(
                recipe=obj, user=user
            ).exists()
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingList.objects.filter(
                recipe=obj, user=user
            ).exists()
        else:
            return False

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

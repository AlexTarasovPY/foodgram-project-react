from rest_framework import viewsets
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from django.db.models import Sum

from .models import (
    Recipe,
    Ingredient,
    Tag,
    FavoriteRecipes,
    ShoppingList,
    RecipeIngredients
)
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    RecipeSerializer,
    RecipeGetSerializer
)
from .permissions import OwnerOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет, обрабатывающий запросы, поступающие на
    эндпойнты, начинающиеся с api/ingredients.
    Позволяет получить информацию об ингредиентах.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет, обрабатывающий запросы, поступающие на
    эндпойнты, начинающиеся с api/tags.
    Позволяет получить информацию о тэгах.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет, обрабатывающий запросы, поступающие на
    эндпойнты, начинающиеся с api/recipes.
    Создание, редактирование, удаление рецептов.
    Получение информации о рецептах.
    """
    permission_classes = (OwnerOrReadOnly,)

    def get_queryset(self):
        tags = self.request.query_params.getlist('tags')
        user = self.request.user
        author = self.request.query_params.get('author')
        is_favorited = self.request.query_params.get('is_favorited', False)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', False
        )
        qs = Recipe.objects.all()
        if tags:
            recipes = list(
                Tag.objects.filter(slug__in=tags).values_list(
                    'recipes', flat=True
                )
            )
            qs = qs.filter(id__in=recipes)
        if user.is_authenticated:
            if is_favorited:
                favorite_recipes = list(
                    FavoriteRecipes.objects.filter(user=user).values_list(
                        'recipe_id', flat=True
                    )
                )
                qs = qs.filter(id__in=favorite_recipes)
            if is_in_shopping_cart:
                shopping_cart_recipes = list(
                    ShoppingList.objects.filter(user=user).values_list(
                        'recipe_id', flat=True))
                qs = qs.filter(id__in=shopping_cart_recipes)
        if author is not None:
            qs = qs.filter(author=author)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False, methods=['GET'], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Метод позволяет выгружать список ингредиентов
        с подсчетом итогового количества для рецептов,
        добавленных в список для покупок.
        Выгрузка реализована в txt-файл.
        """
        purchases = RecipeIngredients.objects.select_related(
            'recipe', 'ingredient'
        )
        purchases = purchases.filter(
            recipe__shoppingcart__user=request.user
        )
        purchases = purchases.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by().values("ingredient__name").annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total_amt=Sum('amount')
        )
        text = '\n'.join([
            f"{item['name']} {item['units']} - {item['total_amt']}"
            for item in purchases
        ])
        filename = 'shopping_list'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        """
        Метод добавляет и удаляет рецепты в список для покупок пользователя.
        """

        if request.method == "POST":
            serializer = ShoppingCartSerializer(
                data=request.data, context={
                    "request": request, "recipe_id": kwargs["pk"]
                })
            if serializer.is_valid():
                recipe = Recipe.objects.get(id=kwargs["pk"])
                serializer.save(user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == "DELETE":
            try:
                shopping_recipe = ShoppingList.objects.get(
                    recipe_id=kwargs["pk"], user=request.user
                )
            except ShoppingList.DoesNotExist:
                raise serializers.ValidationError({
                    'errors': 'Рецепт не существует или отсутствует в корзине'
                })
            shopping_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        """
        Метод добавляет и удаляет рецепты в список избранного пользователя.
        """
        if request.method == "POST":
            serializer = FavoriteSerializer(
                data=request.data,
                context={"request": request, "recipe_id": kwargs["pk"]}
            )
            if serializer.is_valid():
                recipe = Recipe.objects.get(id=kwargs["pk"])
                serializer.save(user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == "DELETE":
            try:
                favorite_recipe = FavoriteRecipes.objects.get(
                    recipe_id=kwargs["pk"], user=request.user
                )
            except FavoriteRecipes.DoesNotExist:
                raise serializers.ValidationError({
                    'errors': 'Рецепт не существует или '
                    + 'отсутствует в избранном'
                })
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

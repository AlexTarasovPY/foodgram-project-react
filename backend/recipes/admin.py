from django.contrib import admin


from .models import (
    Recipe,
    Subscribe,
    Tag,
    Ingredient,
    FavoriteRecipes,
    ShoppingList,
    RecipeIngredients,
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'author', 'pub_date', 'name',
        'text', 'cooking_time',
        'image', 'favorite_count',
    )
    list_editable = (
        'author', 'name',
        'text', 'cooking_time', 'image',
    )
    read_only_fields = (
        'favorite_count',
    )
    search_fields = ('author__username', 'name', 'tags__slug',)
    empty_value_display = '-пусто-'

    def favorite_count(self, obj):
        return FavoriteRecipes.objects.filter(recipe=obj).count()
    favorite_count.short_description = 'Добавлено в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'measurement_unit',
    )
    list_editable = (
        'name', 'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'user', 'subscribed',
    )
    list_editable = (
        'user', 'subscribed',
    )
    search_fields = ('user__username', 'subscribed__username')
    empty_value_display = '-пусто-'


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'user', 'recipe',
    )
    list_editable = (
        'user', 'recipe',
    )
    search_fields = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'color', 'slug'
    )
    list_editable = (
        'name', 'color', 'slug',
    )
    search_fields = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'user', 'recipe',
    )
    list_editable = (
        'user', 'recipe',
    )
    search_fields = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'


class RecipeingredientsAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'recipe', 'ingredient', 'amount',
    )
    list_editable = (
        'recipe', 'ingredient', 'amount',
    )
    search_fields = ('recipe__name', 'ingredient__name')
    empty_value_display = '-пусто-'


admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(FavoriteRecipes, FavoriteRecipesAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredients, RecipeingredientsAdmin)

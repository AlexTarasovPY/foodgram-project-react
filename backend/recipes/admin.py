from django.contrib import admin
from .models import Recipe, Subscribe, Tag, Ingredient, FavoriteRecipes
from .models import ShoppingList, RecipeIngredients, RecipeTags


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


admin.site.register(Subscribe)
admin.site.register(Tag)
admin.site.register(RecipeIngredients)
admin.site.register(ShoppingList)
admin.site.register(FavoriteRecipes)
admin.site.register(RecipeTags)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)

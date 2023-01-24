from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    subscribed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribed'],
                name='unique_subscribe'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscribed')),
                name='do_not_subscribe_to_yourself',
            ),
        ]


class Tag(models.Model):
    name = models.TextField(verbose_name='тэг')
    color = models.TextField(verbose_name='Цветовой HEX-код')
    slug = models.SlugField(unique=True, verbose_name='Ссылка на тег')


class Ingredient(models.Model):
    name = models.TextField(verbose_name='Наименование ингредиента')
    measurement_unit = models.TextField(verbose_name='Единица измерения')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.TextField(verbose_name='Наименование блюда')
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=True
    )
    text = models.TextField(verbose_name='Описание блюда')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.'
    )
    tags = models.ManyToManyField(Tag, through='RecipeTags')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredients'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipeingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента'
    )


class RecipeTags(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            ),

        ]


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shoppingcart'
    )

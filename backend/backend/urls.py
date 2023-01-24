
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from recipes.views import IngredientViewSet, TagViewSet, RecipeViewSet
from recipes.views import FavoriteView, ShoppingCartView
from recipes.views import DownloadShoppingCartView
from users.views import SubscribeView, SubscriptionsView

router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/recipes/<int:recipe_id>/favorite/',
        FavoriteView.as_view(), name='favorite'
    ),
    path(
        'api/recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartView.as_view(), name='shopping_cart'
    ),
    path(
        'api/recipes/download_shopping_cart/',
        DownloadShoppingCartView.as_view(), name='download_shopping_cart'
    ),
    path('api/auth/', include('djoser.urls.authtoken')),
    path(
        'api/users/<int:user_id>/subscribe/',
        SubscribeView.as_view(), name='subscribe'
    ),
    path(
        'api/users/subscriptions/',
        SubscriptionsView.as_view(), name='subscriptions'
    ),
    path('api/', include(router_v1.urls)),
    path('api/', include('djoser.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from recipes.views import IngredientViewSet, TagViewSet, RecipeViewSet
from users.views import SubscribeView, SubscriptionsView

router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),
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

]

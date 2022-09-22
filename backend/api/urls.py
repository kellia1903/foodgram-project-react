from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register(r'users', UserViewSet, basename='users')
router.register('tags', TagViewSet)

subscriptions = UserViewSet.as_view({'get': 'subscriptions', })

urlpatterns = [
    path('users/subscriptions/', subscriptions, name='subscriptions'),
    path('', include('djoser.urls'), name='djoser'),
    path('auth/', include('djoser.urls.authtoken'), name='djoser-authtoken'),
    path('', include(router.urls), name='api')
]
# gghhjj

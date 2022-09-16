from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag, User)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import AuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, UserFollowSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, ]
    filter_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = LimitPageNumberPagination
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AuthorOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
    filter_class = RecipeFilter

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        permission_classes=[IsAuthenticated, ],
        url_path='favorite'
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'GET':
            favorite_recipe, created = FavoriteRecipe.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created is True:
                serializer = FavoriteSerializer()
                return Response(
                    serializer.to_representation(instance=favorite_recipe),
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            favorite_recipe = FavoriteRecipe.objects.filter(
                user=user,
                recipe=recipe
            )
            if favorite_recipe.exists() is True:
                favorite_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Такого рецепта нет в избранном'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            recipe, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created is True:
                serializer = ShoppingCartSerializer()
                return Response(
                    serializer.to_representation(instance=recipe),
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Рецепт уже в корзине покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            recipe_in_cart = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            )
            if recipe_in_cart.exists() is True:
                recipe_in_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Такого рецепта нет в списке'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        try:
            shopping_cart = ShoppingCart.objects.filter(
                user=request.user).all()
            shopping_list = {}
            for item in shopping_cart:
                for recipe_ingredient in item.recipe.recipe_ingredients.all():
                    name = recipe_ingredient.ingredient.name
                    measuring_unit = (
                        recipe_ingredient.ingredient.measurement_unit
                    )
                    amount = recipe_ingredient.amount
                    if name not in shopping_list:
                        shopping_list[name] = {
                            'name': name,
                            'measurement_unit': measuring_unit,
                            'amount': amount
                        }
                    else:
                        shopping_list[name]['amount'] += amount
            content = (
                [f'{item["name"]} ({item["measurement_unit"]}) '
                 f'- {item["amount"]}\n'
                 for item in shopping_list.values()]
            )
            response = HttpResponse(content, content_type='text/plain')
            response['Content-Disposition'] = (
                'attachment; filename="shopping_list.txt"'
            )
            return response
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ]
    )
    def subscribe(self, request, pk):
        followed = get_object_or_404(User, id=pk)
        follower = request.user
        subscribed = followed.subscriptions.filter(
                     username=follower.username
                     ).exists()

        if request.method == 'POST':
            if followed == follower:
                return Response(
                    {'errors': 'Вы не можете подписываться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscribed:
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            followed.subscriptions.add(follower)
            serializer = UserFollowSerializer(
                context=self.get_serializer_context()
            )
            return Response(serializer.to_representation(
                instance=followed),
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if followed == follower:
                return Response(
                    {'errors': 'Вы не можете отписаться от самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscribed:
                followed.subscriptions.remove(follower)
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы уже отписались'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=[IsAuthenticated, ],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        followed_list = User.objects.filter(subscriptions=request.user)
        pages = self.paginate_queryset(followed_list)
        serializer = UserFollowSerializer(
            pages,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

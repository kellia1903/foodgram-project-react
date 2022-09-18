from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag, User)
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

    def favorite_or_shopping_cart_method(self, request, pk, model,
                                         serializer, error_already, error_no):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            using_recipe, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created:
                return Response(
                    serializer.to_representation(instance=using_recipe),
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': error_already},
                status=status.HTTP_400_BAD_REQUEST
            )
        used_recipe = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if used_recipe.exists():
            used_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': error_no},
            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ],
        url_path='favorite'
    )
    def favorite(self, request, pk):
        model = FavoriteRecipe
        serializer = FavoriteSerializer()
        error_already = 'Рецепт уже в избранном'
        error_no = 'Такого рецепта нет в избранном'
        return self.favorite_or_shopping_cart_method(
            request, pk, model, serializer, error_already, error_no
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        model = ShoppingCart
        serializer = ShoppingCartSerializer()
        error_already = 'Рецепт уже в корзине покупок'
        error_no = 'Такого рецепта нет в списке'
        return self.favorite_or_shopping_cart_method(
            request, pk, model, serializer, error_already, error_no
        )

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=request.user
        ).order_by(
            'ingredient__name'
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(sum_amount=Sum('amount'))
        shopping_cart = '\n'.join([
            f'{ingredient["ingredient__name"]} - {ingredient["sum_amount"]}'
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        ])
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


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

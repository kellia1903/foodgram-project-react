from djoser.serializers import \
    UserCreateSerializer as BaseUserRegistrationSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag, User)
from rest_framework import serializers, validators


class FollowerRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return self.context.get('request').user in obj.subscriptions.all()


class UserFollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField('get_recipes_count')
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return self.context.get('request').user in obj.subscriptions.all()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj)
        if limit:
            queryset = queryset[:int(limit)]
        return FollowerRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    slug = serializers.SlugField()

    class Meta:
        model = Tag
        fields = '__all__'
        lookup_field = 'slug'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=RecipeIngredient.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    name = serializers.CharField(required=True)
    tags = TagSerializer(read_only=True, many=True)
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(max_value=1440, min_value=1)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужно выбрать хотя бы один ингредиент!'
            })
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными!'
                })
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': 'Количество ингредиента должно быть больше нуля!'
                })

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужно выбрать хотя бы один тэг!'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Тэги должны быть уникальными!'
                })
            tags_list.append(tag)

        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше 0!'
            })

        return data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated and
                user.favorites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated and
                user.shopping_carts.filter(recipe=obj).exists())
    
    def create(self, validated_data):
        context = self.context['request']
        ingredients = context.data['ingredients']
        tags = context.data['tags']
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount'],
            )
        print(recipe)
        return recipe
    
    def update(self, instance, validated_data):
        context = self.context['request']
        ingredients = context.data['ingredients']
        tags = context.data['tags']
        recipe = instance
        instance.name = validated_data.pop('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.pop('cooking_time')
        if validated_data.get('image') is not None:
            instance.image = validated_data.get('image')
        instance.save()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount'],
            )
        return instance

    def to_representation(self, instance):
        response = super(RecipeSerializer, self).to_representation(instance)
        if instance.image:
            response['image'] = instance.image.url
        return response


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True,
        source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True,
        source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True,
        source='recipe.name',
    )

    class Meta:
        model = FavoriteRecipe
        fields = (
            'id',
            'cooking_time',
            'name',
            'image'
        )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def create(self, validated_data):
        favorite = FavoriteRecipe.objects.create(**validated_data)
        favorite.save()
        return favorite


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True,
        source='recipe.id',
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source='recipe.cooking_time',
    )
    image = serializers.CharField(
        read_only=True,
        source='recipe.image',
    )
    name = serializers.CharField(
        read_only=True,
        source='recipe.name',
    )

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'cooking_time',
            'name',
            'image'
        )    

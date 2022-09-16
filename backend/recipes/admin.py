from django.contrib.admin import ModelAdmin, site

from .models import Ingredient, Recipe, ShoppingCart, Tag, User


class UserAdmin(ModelAdmin):
    list_filter = ('username', 'email')


class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'added_in_favorites')
    list_filter = ('author', 'name', 'tags',)
    readonly_fields = ('added_in_favorites',)
    empty_value_display = '-пусто-'

    def added_in_favorites(self, obj):
        return obj.favorites.count()

    added_in_favorites.short_description = 'Популярность'


class TagAdmin(ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color',)
    search_fields = ('name', 'slug',)
    ordering = ('color',)
    empty_value_display = '-пусто-'


class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('measurement_unit',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(ModelAdmin):
    list_display = ('id', 'user', 'recipe')


site.register(User, UserAdmin)
site.register(Recipe, RecipeAdmin)
site.register(Tag, TagAdmin)
site.register(Ingredient, IngredientAdmin)
site.register(ShoppingCart, ShoppingCartAdmin)

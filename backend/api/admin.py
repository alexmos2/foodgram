from django.contrib import admin


from .models import (
    Subscription, Tag, Receipt, Ingredient, ShoppingList, Favorite)


class AdminSub(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )


class AdminTag(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug'
    )


class AdminIngredient(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


class AdminReceipt(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'get_tags',
        'get_ingredients',
        'favorite_count'
    )
    search_fields = (
        'name',
        'author__username',
    )
    list_filter = ('tags',)
    readonly_fields = ('favorite_count',)

    def favorite_count(self, instance):
        return instance.favorites_of_users.count()

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def get_ingredients(self, obj):
        return ", ".join(
            [ingredient.name for ingredient in obj.ingredients.all()])
    get_ingredients.short_description = 'Ingredients'


class AdminFavorite(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'receipt'
    )


class AdminShoppingList(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'receipt'
    )


admin.site.register(Subscription, AdminSub)
admin.site.register(Tag, AdminTag)
admin.site.register(Ingredient, AdminIngredient)
admin.site.register(Favorite, AdminFavorite)
admin.site.register(Receipt, AdminReceipt)
admin.site.register(ShoppingList, AdminShoppingList)

from django.contrib import admin

# Register your models here.

from .models import (
    Subscription, User, Tag, Receipt, Ingredient, ShoppingList, Favorite)


class AdminUser(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username', 'email')


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
    search_fields = ('name')


class AdminReceipt(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author'
    )
    search_fields = (
        'name',
        'author__username',
    )
    list_filter = ('tag',)
    readonly_fields = ('favorite_count',)

    def favorite_count(self, instance):
        return instance.favorites_of_users.count()


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


admin.site.register(User, AdminUser)
admin.site.register(Subscription, AdminSub)
admin.site.register(Tag, AdminTag)
admin.site.register(Ingredient, AdminIngredient)
admin.site.register(Favorite, AdminFavorite)
admin.site.register(Receipt, AdminReceipt)
admin.site.register(ShoppingList, AdminShoppingList)

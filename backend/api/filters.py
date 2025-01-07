from django_filters.rest_framework import FilterSet, filters

from .models import Ingredient, Receipt


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class TagFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_by_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_by_shopping_cart')

    class Meta:
        model = Receipt
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_by_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites_of_users__user=self.request.user)
        return queryset if not value else queryset.none()

    def filter_by_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset if not value else queryset.none()

from rest_framework import serializers, validators
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.db import transaction
from rest_framework.exceptions import NotAuthenticated

from .models import (Tag, Ingredient, Receipt, IngredientReceipt,
                     User, Favorite, ShoppingList, Subscription)
from .fields import Base64ImageField


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientReceiptSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientReceipt
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = (
            validators.UniqueTogetherValidator(
                queryset=IngredientReceipt.objects.all(),
                fields=('ingredient', 'receipt')
            ),
        )

    def __str__(self):
        return f'{self.ingredient} содержится в {self.receipt}'


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientReceipt
        fields = ('id', 'amount')


class MyUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.following.filter(author=obj).exists()

    def to_representation(self, instance):
        request = self.context.get('request')
        if request:
            if request.path.endswith('/users/me/'):
                if not request.user.is_authenticated:
                    raise NotAuthenticated(
                        detail='Authentication credentials were not provided.')
        return super().to_representation(instance)


class MyUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = SubscriptionSerializer(
            instance,
            context=context
        )
        return serializer.data

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='author.author_receipts.count')

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return request.user.following.filter(author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = obj.author.author_receipts.all()
        if request.GET.get('recipes_limit'):
            receipt_limit = int(request.GET.get('recipes_limit'))
            queryset = queryset[:receipt_limit]
        serializer = ShortReceiptSerializer(
            queryset, read_only=True, many=True
        )
        return serializer.data

    def get_avatar(self, obj):
        if obj.author.avatar:
            return obj.author.avatar
        return None


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class TagField(serializers.SlugRelatedField):

    def to_representation(self, value):
        request = self.context.get('request')
        context = {'request': request}
        serializer = TagSerializer(value, context=context)
        return serializer.data


class ReceiptSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientReceiptSerializer(
        source='receipts', many=True)
    author = MyUserSerializer()
    tags = TagField(
        slug_field='id', queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Receipt
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'ingredients', 'tags', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = ('author',)

    def is_included(self, obj, model):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, receipt=obj).exists()

    def get_is_favorited(self, obj):
        return self.is_included(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.is_included(obj, ShoppingList)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class AddReceiptSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Receipt
        fields = (
            'tags',
            'name',
            'ingredients',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        serializer = ReceiptSerializer(instance)
        return serializer.data

    def create_ingredients(self, ingredients, receipt):
        ingredient_receipts = [
            IngredientReceipt(
                receipt=receipt,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients
        ]
        IngredientReceipt.objects.bulk_create(ingredient_receipts)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        receipt = Receipt.objects.create(**validated_data)
        if tags and tags != []:
            receipt.tags.set(tags)
        if ingredients and ingredients != []:
            self.create_ingredients(ingredients, receipt)
        return receipt

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        if ingredients and ingredients != []:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if tags and tags != []:
            instance.tags.set(tags, clear=True)
        return super().update(instance, validated_data)

    def validate(self, data):
        def contains_duplicates(seq):
            seen = []
            return any(i in seen or seen.append(i) for i in seq)
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                'Поле с ингредиентами отсутствует'
            )
        if 'tags' not in data:
            raise serializers.ValidationError(
                'Поле с тегами отсутствует'
            )
        if 'cooking_time' not in data:
            raise serializers.ValidationError(
                'Поле с временем готовки отсутствует'
            )
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError(
                'Поле с ингредиентами должно иметь значение'
            )
        for ingredient in ingredients:
            if not isinstance(ingredient['amount'], int):
                raise serializers.ValidationError(
                    'Недопустимое нецелое значение'
                )
        if contains_duplicates(ingredients):
            raise serializers.ValidationError(
                'В рецепте не должно быть повторяющихся ингредиентов'
            )
        tags = data['tags']
        if tags == []:
            raise serializers.ValidationError(
                'В рецепте должен быть хотя бы один тег'
            )
        if contains_duplicates(tags):
            raise serializers.ValidationError(
                'В рецепте не должно быть повторяющихся тегов'
            )
        cooking_time = data['cooking_time']
        if not cooking_time:
            raise serializers.ValidationError(
                'Поле с временем готовки не может быть пустым'
            )
        return data


class ShortReceiptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Receipt
        fields = ('id', 'name', 'image', 'cooking_time')

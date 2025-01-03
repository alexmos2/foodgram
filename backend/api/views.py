from django.db.models import Sum
from rest_framework import status, viewsets, views, filters, mixins
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from django.shortcuts import get_object_or_404

from .models import (Receipt, Tag, Ingredient, Favorite,
                     IngredientReceipt, ShoppingList,
                     Subscription, User)
from .serializers import (ReceiptSerializer, TagSerializer,
                          IngredientSerializer,
                          AddReceiptSerializer, ShortReceiptSerializer,
                          SubscribeSerializer, SubscriptionSerializer,
                          UserAvatarSerializer)
from .filters import IngredientFilter, TagFilter
from .permissions import IsOwnerOrReadOnly
from .pagination import ReceiptPagination


class ReceiptShortLinkView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        receipt = get_object_or_404(Receipt, pk=pk)
        if receipt.short_link:
            short_url = request.build_absolute_uri(
                f'/api/short/{receipt.short_link}')
            return Response(
                {"short-link": short_url}, status=status.HTTP_200_OK)
        receipt.short_link = receipt.generate_short_link()
        receipt.save()
        short_url = request.build_absolute_uri(
            f'/api/short/{receipt.short_link}')
        return Response({"short-link": short_url}, status=status.HTTP_200_OK)


class ReceiptMixin:
    def add_receipt(self, request, pk, table):
        receipt = get_object_or_404(Receipt, pk=pk)
        user = request.user
        if table.objects.filter(receipt=receipt, user=user).exists():
            raise ValidationError({'detail': 'Рецепт уже есть в этом списке'})
        table.objects.create(receipt=receipt, user=user)
        serializer = ShortReceiptSerializer(receipt)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_receipt(self, request, pk, table):
        receipt = get_object_or_404(Receipt, pk=pk)
        user = request.user
        deleting_object = table.objects.filter(
            user=user, receipt=receipt).first()
        if not deleting_object:
            raise ValidationError({'detail': 'Объект не существует'})
        deleting_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShortLinkRedirectView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, short_link):
        receipt = get_object_or_404(Receipt, short_link=short_link)
        return HttpResponseRedirect(f'/recipes/{receipt.id}/')


class UserAvatarViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAvatarSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        return Response({'avatar': user.avatar.url if user.avatar else None})

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.data == {}:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReceiptViewSet(viewsets.ModelViewSet, ReceiptMixin):
    queryset = Receipt.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = ReceiptPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReceiptSerializer
        return AddReceiptSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_receipt(request, pk, Favorite)
        else:
            return self.delete_receipt(request, pk, Favorite)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientReceipt.objects.filter(
            receipt__shopping_list__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        file_name = 'shopping_list.txt'
        header = "{:<30} {:<20} {:<10}".format(
            "Ингредиент", "Мера измерения", "Количество")
        lines = [header, "-" * len(header)]  # Заголовок и разделитель
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_total']
            line = "{:<30} {:<20} {:<10}".format(
                name, measurement_unit, amount)
            lines.append(line)
        lines.append('\nAlexMos Production')
        content = '\n'.join(lines)
        content_type = 'text/plain;charset=utf-8'
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_receipt(request, pk, ShoppingList)
        else:
            return self.delete_receipt(request, pk, ShoppingList)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = IngredientFilter
    pagination_class = None

    search_fields = ['name']


class SubscriptionViewSet(ListAPIView):
    serializer_class = SubscriptionSerializer
    pagination_class = ReceiptPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()


class SubscribeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get_author(self, pk):
        return get_object_or_404(User, pk=pk)

    def post(self, request, pk):
        author = self.get_author(pk)
        user = request.user
        if user == author:
            return Response(
                {'detail': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SubscribeSerializer(
            data={'author': author.id, 'user': user.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = self.get_author(pk)
        user = request.user
        subscription = Subscription.objects.filter(
            user=user, author=author).first()
        if not subscription:
            return Response(
                {'detail': 'Подписка не существует.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from django.urls import include, path
from rest_framework import routers
from django.views.generic import TemplateView

from .views import (ReceiptViewSet, TagViewSet, IngredientViewSet,
                    SubscribeView, SubscriptionViewSet,
                    UserAvatarViewSet, ReceiptShortLinkView)
from users.views import CustomUserViewSet

router = routers.DefaultRouter()
router.register(r'recipes', ReceiptViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('users/me/', CustomUserViewSet.as_view(
        {'get': 'retrieve'})),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view()),
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path(
        'recipes/<int:pk>/get-link/',
        ReceiptShortLinkView.as_view(),
        name='receipt-get-link'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path(
        'users/me/avatar/', UserAvatarViewSet.as_view(
            {
                'get': 'retrieve',
                'post': 'create',
                'put': 'update',
                'delete': 'destroy'
            }
        )
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'docs/',
        TemplateView.as_view
        (
            template_name='usr/share/nginx/html/api/docs/redoc.html'
        ),
        name='redoc'
    ),
]

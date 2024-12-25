from api.views import (ReceiptViewSet, TagViewSet, IngredientViewSet,
                       SubscribeView, SubscriptionViewSet,
                       UserAvatarViewSet, ReceiptShortLinkView,
                       ShortLinkRedirectView)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register(r'recipes', ReceiptViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    path(
        'api/short/<str:short_link>/',
        ShortLinkRedirectView.as_view(),
        name='short-link-redirect'
    ),
    path('api/users/<int:pk>/subscribe/', SubscribeView.as_view()),
    path('api/users/subscriptions/', SubscriptionViewSet.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path(
        'api/recipes/<int:pk>/get-link/',
        ReceiptShortLinkView.as_view(),
        name='receipt-get-link'
    ),
    path('api/', include('djoser.urls')),  # Работа с пользователями
    path(
        'api/users/me/avatar/', UserAvatarViewSet.as_view(
            {
                'get': 'retrieve',
                'post': 'create',
                'put': 'update',
                'delete': 'destroy'
            }
        )
    ),
    path('api/auth/', include('djoser.urls.authtoken')),  # Работа с токенами
    path(
        'api/docs/',
        TemplateView.as_view
        (
            template_name='usr/share/nginx/html/api/docs/redoc.html'
        ),
        name='redoc'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

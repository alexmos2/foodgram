from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet
from rest_framework.response import Response


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticated, )

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(request.user).data)

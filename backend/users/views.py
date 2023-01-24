from rest_framework.views import APIView
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination

from recipes.models import Subscribe
from .serializers import SubscribeSerializer

User = get_user_model()


class SubscribeView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = SubscribeSerializer(
            data=request.data,  context={
                "request": request, "user_id": self.kwargs.get("user_id")
            }
        )
        if serializer.is_valid():
            try:
                subscribed = User.objects.get(
                    id=self.kwargs.get("user_id")
                )
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'errors': 'Пользователь с указанным id не существует.'
                })
            if Subscribe.objects.filter(
                user=request.user, subscribed=subscribed
            ).exists():
                raise serializers.ValidationError({
                    'errors': 'Вы уже подписаны на этого пользователя.'
                })
            if subscribed == request.user:
                raise serializers.ValidationError({
                    'errors': 'Нельзя подписываться на себя.'
                })
            serializer.save(user=request.user, subscribed=subscribed)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        try:
            subscribe = Subscribe.objects.get(
                user=request.user, subscribed_id=self.kwargs.get("user_id")
            )
        except Subscribe.DoesNotExist:
            raise serializers.ValidationError({
                'errors': 'Вы не подписаны на пользователя'
            })
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(APIView, LimitOffsetPagination):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        subscribes = Subscribe.objects.filter(user=request.user)

        result_page = self.paginate_queryset(subscribes, request, view=self)
        serializer = SubscribeSerializer(
            result_page, many=True,  context={
                "request": request,
            }
        )
        return self.get_paginated_response(serializer.data)

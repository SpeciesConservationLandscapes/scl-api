from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.viewsets import GenericViewSet

from .base import BaseAPISerializer
from ..models import Profile


class ProfileSerializer(BaseAPISerializer):
    countries = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        exclude = []

    def get_countries(self, obj):
        return [dict(code=c.code, name=c.name) for c in obj.countries]


class MeViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        pass

    def list(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.profile
        if profile is None:
            raise NotFound()

        return Response(self.serializer_class(profile).data)

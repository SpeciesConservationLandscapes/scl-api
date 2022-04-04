from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from .base import BaseAPIFilterSet, LandscapeSerializer, StatsSerializer, StatsViewSet
from ..models import SCL, SCLStats


class SCLSerializer(LandscapeSerializer):

    class Meta:
        model = SCL
        exclude = []


class SCLStatsSerializer(StatsSerializer):
    scl = SCLSerializer()

    class Meta(StatsSerializer.Meta):
        model = SCLStats
        fields = ["id", "country", "scl", "geom", "area", "biome_areas"]


class SCLStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = SCLStats
        fields = ["country", "scl__species", "scl__date", "scl__name", "scl__lsid"]


class SCLStatsViewSet(StatsViewSet):
    serializer_class = SCLStatsSerializer
    filter_class = SCLStatsFilterSet
    ordering_fields = ["country", "scl__species", "scl__date", "scl__name", "scl__lsid"]
    queryset = SCLStats.objects.select_related()

    @action(detail=False, methods=["get"])
    def available_dates(self, request):
        filters = {}
        country = request.query_params.get("country")
        species = request.query_params.get("scl__species")
        if country:
            filters["country"] = country
        if species:
            filters["scl__species"] = species

        qs = SCLStats.objects.filter(**filters)
        _available_dates = (
            qs.order_by("scl__date").values_list("scl__date", flat=True).distinct()
        )

        return Response(_available_dates)

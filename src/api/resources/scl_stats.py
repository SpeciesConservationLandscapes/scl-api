from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from .base import BaseAPIFilterSet, LandscapeSerializer, StatsSerializer, StatsViewSet
from ..models import SCL, SCLStats


class SCLSerializer(LandscapeSerializer):
    sclclass = serializers.SerializerMethodField()

    class Meta:
        model = SCL
        exclude = []

    @staticmethod
    def get_sclclass(obj):
        return dict(SCL.CLASS_CHOICES)[obj.sclclass]


class SCLStatsSerializer(StatsSerializer):
    scl = SCLSerializer()

    class Meta(StatsSerializer.Meta):
        model = SCLStats
        fields = ["id", "country", "scl", "geom", "area", "biome_areas"]


class SCLStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = SCLStats
        fields = ["country", "scl__species", "scl__date", "scl__name"]


class SCLStatsViewSet(StatsViewSet):
    serializer_class = SCLStatsSerializer
    filter_class = SCLStatsFilterSet
    ordering_fields = ["country", "scl__species", "scl__date", "scl__name"]
    required_filters = ["country", "scl__species", "scl__date"]

    def get_queryset(self):
        for f in self.required_filters:
            if (
                f not in self.request.query_params
                or self.request.query_params[f] is None
                or self.request.query_params[f] == ""
            ):
                return SCLStats.objects.none()

        filters = {
            "country": self.request.query_params["country"],
            "scl__species": self.request.query_params["scl__species"],
            "scl__date": self.request.query_params["scl__date"],
        }

        return SCLStats.objects.filter(**filters).select_related()
    

    @action(detail=False, methods=["get"])
    def available_dates(self, request):
        if "country" not in self.request.query_params or "scl__species" not in self.request.query_params:
            return SCLStats.objects.none()

        qs = SCLStats.objects.filter(
            country=request.query_params["country"],
            scl__species=request.query_params["scl__species"]
        )
        available_dates = qs.order_by("scl__date").values_list("scl__date", flat=True).distinct()

        return Response(available_dates)

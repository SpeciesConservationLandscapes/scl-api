from rest_framework import serializers
from rest_framework_gis.pagination import GeoJsonPagination
from .base import BaseAPIFilterSet, BaseAPIViewSet, LandscapeSerializer, StatsSerializer
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
        fields = ["id", "country", "date", "scl", "geom", "biome_areas"]


class SCLStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = SCLStats
        fields = ["country", "scl__species", "date", "scl__name"]


class SCLStatsViewSet(BaseAPIViewSet):
    pagination_class = GeoJsonPagination
    serializer_class = SCLStatsSerializer
    filter_class = SCLStatsFilterSet
    ordering_fields = ["country", "scl__species", "date", "scl__name"]
    required_filters = ["country", "scl__species", "date"]

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
            "date": self.request.query_params["date"],
        }

        return SCLStats.objects.filter(**filters).select_related()

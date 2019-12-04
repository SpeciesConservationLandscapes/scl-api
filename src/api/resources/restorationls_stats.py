from django.contrib.gis.db.models.functions import Area
from rest_framework import serializers
from rest_framework_gis.pagination import GeoJsonPagination
from .base import BaseAPIFilterSet, BaseAPISerializer, BaseAPIViewSet, StatsSerializer
from ..models import RestorationLandscape, RestorationStats


class RestorationSerializer(BaseAPISerializer):
    species = serializers.SerializerMethodField()

    class Meta:
        model = RestorationLandscape
        exclude = []

    @staticmethod
    def get_species(obj):
        return str(obj.species)


class RestorationStatsSerializer(StatsSerializer):
    restoration_landscape = RestorationSerializer()

    class Meta(StatsSerializer.Meta):
        model = RestorationStats
        fields = [
            "id",
            "country",
            "date",
            "biome",
            "pa",
            "restoration_landscape",
            "geom",
            "area_km2",
        ]


class RestorationStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = RestorationStats
        fields = [
            "country",
            "restoration_landscape__species",
            "date",
            "biome__name",
            "pa__name",
        ]


class RestorationStatsViewSet(BaseAPIViewSet):
    pagination_class = GeoJsonPagination
    serializer_class = RestorationStatsSerializer
    filter_class = RestorationStatsFilterSet
    ordering_fields = [
        "country",
        "restoration_landscape__species",
        "date",
        "biome__name",
        "pa__name",
    ]
    required_filters = ["country", "restoration_landscape__species", "date"]

    def get_queryset(self):
        for f in self.required_filters:
            if (
                f not in self.request.query_params
                or self.request.query_params[f] is None
                or self.request.query_params[f] == ""
            ):
                return RestorationStats.objects.none()

        filters = {
            "country": self.request.query_params["country"],
            "restoration_landscape__species": self.request.query_params[
                "restoration_landscape__species"
            ],
            "date": self.request.query_params["date"],
        }

        return (
            RestorationStats.objects.filter(**filters)
            .annotate(area=Area("geom"))
            .select_related()
        )

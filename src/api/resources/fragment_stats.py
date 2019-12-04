from django.contrib.gis.db.models.functions import Area
from rest_framework import serializers
from rest_framework_gis.pagination import GeoJsonPagination
from .base import BaseAPIFilterSet, BaseAPISerializer, BaseAPIViewSet, StatsSerializer
from ..models import FragmentLandscape, FragmentStats


class FragmentSerializer(BaseAPISerializer):
    species = serializers.SerializerMethodField()

    class Meta:
        model = FragmentLandscape
        exclude = []

    @staticmethod
    def get_species(obj):
        return str(obj.species)


class FragmentStatsSerializer(StatsSerializer):
    fragment = FragmentSerializer()

    class Meta(StatsSerializer.Meta):
        model = FragmentStats
        fields = [
            "id",
            "country",
            "date",
            "biome",
            "pa",
            "fragment",
            "geom",
            "area_km2",
        ]


class FragmentStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = FragmentStats
        fields = ["country", "fragment__species", "date", "biome__name", "pa__name"]


class FragmentStatsViewSet(BaseAPIViewSet):
    pagination_class = GeoJsonPagination
    serializer_class = FragmentStatsSerializer
    filter_class = FragmentStatsFilterSet
    ordering_fields = [
        "country",
        "fragment__species",
        "date",
        "biome__name",
        "pa__name",
    ]
    required_filters = ["country", "fragment__species", "date"]

    def get_queryset(self):
        for f in self.required_filters:
            if (
                f not in self.request.query_params
                or self.request.query_params[f] is None
                or self.request.query_params[f] == ""
            ):
                return FragmentStats.objects.none()

        filters = {
            "country": self.request.query_params["country"],
            "fragment__species": self.request.query_params["fragment__species"],
            "date": self.request.query_params["date"],
        }

        return (
            FragmentStats.objects.filter(**filters)
            .annotate(area=Area("geom"))
            .select_related()
        )

from django.contrib.gis.db.models.functions import Area
from rest_framework import serializers
from rest_framework_gis.pagination import GeoJsonPagination
from .base import BaseAPIFilterSet, BaseAPISerializer, BaseAPIViewSet, StatsSerializer
from ..models import SurveyLandscape, SurveyStats


class SurveySerializer(BaseAPISerializer):
    species = serializers.SerializerMethodField()

    class Meta:
        model = SurveyLandscape
        exclude = []

    @staticmethod
    def get_species(obj):
        return str(obj.species)


class SurveyStatsSerializer(StatsSerializer):
    survey_landscape = SurveySerializer()

    class Meta(StatsSerializer.Meta):
        model = SurveyStats
        fields = [
            "id",
            "country",
            "date",
            "biome",
            "pa",
            "survey_landscape",
            "geom",
            "area_km2",
        ]


class SurveyStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = SurveyStats
        fields = [
            "country",
            "survey_landscape__species",
            "date",
            "biome__name",
            "pa__name",
        ]


class SurveyStatsViewSet(BaseAPIViewSet):
    pagination_class = GeoJsonPagination
    serializer_class = SurveyStatsSerializer
    filter_class = SurveyStatsFilterSet
    ordering_fields = [
        "country",
        "survey_landscape__species",
        "date",
        "biome__name",
        "pa__name",
    ]
    required_filters = ["country", "survey_landscape__species", "date"]

    def get_queryset(self):
        for f in self.required_filters:
            if (
                f not in self.request.query_params
                or self.request.query_params[f] is None
                or self.request.query_params[f] == ""
            ):
                return SurveyStats.objects.none()

        filters = {
            "country": self.request.query_params["country"],
            "survey_landscape__species": self.request.query_params[
                "survey_landscape__species"
            ],
            "date": self.request.query_params["date"],
        }

        return (
            SurveyStats.objects.filter(**filters)
            .annotate(area=Area("geom"))
            .select_related()
        )

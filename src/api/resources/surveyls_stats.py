from rest_framework_gis.pagination import GeoJsonPagination
from .base import BaseAPIFilterSet, BaseAPIViewSet, LandscapeSerializer, StatsSerializer
from ..models import SurveyLandscape, SurveyStats


class SurveySerializer(LandscapeSerializer):
    class Meta:
        model = SurveyLandscape
        exclude = []


class SurveyStatsSerializer(StatsSerializer):
    survey_landscape = SurveySerializer()

    class Meta(StatsSerializer.Meta):
        model = SurveyStats
        fields = ["id", "country", "date", "survey_landscape", "geom", "areas"]


class SurveyStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = SurveyStats
        fields = ["country", "survey_landscape__species", "date"]


class SurveyStatsViewSet(BaseAPIViewSet):
    pagination_class = GeoJsonPagination
    serializer_class = SurveyStatsSerializer
    filter_class = SurveyStatsFilterSet
    ordering_fields = ["country", "survey_landscape__species", "date"]
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

        return SurveyStats.objects.filter(**filters).select_related()

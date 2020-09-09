from .base import BaseAPIFilterSet, LandscapeSerializer, StatsSerializer, StatsViewSet
from ..models import SurveyLandscape, SurveyStats


class SurveySerializer(LandscapeSerializer):
    class Meta:
        model = SurveyLandscape
        exclude = []


class SurveyStatsSerializer(StatsSerializer):
    survey_landscape = SurveySerializer()

    class Meta(StatsSerializer.Meta):
        model = SurveyStats
        fields = ["id", "country", "survey_landscape", "geom", "area", "biome_areas"]


class SurveyStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = SurveyStats
        fields = ["country", "survey_landscape__species", "survey_landscape__date"]


class SurveyStatsViewSet(StatsViewSet):
    serializer_class = SurveyStatsSerializer
    filter_class = SurveyStatsFilterSet
    ordering_fields = ["country", "survey_landscape__species", "survey_landscape__date"]
    required_filters = [
        "country",
        "survey_landscape__species",
        "survey_landscape__date",
    ]

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
            "survey_landscape__date": self.request.query_params[
                "survey_landscape__date"
            ],
        }

        return SurveyStats.objects.filter(**filters).select_related()

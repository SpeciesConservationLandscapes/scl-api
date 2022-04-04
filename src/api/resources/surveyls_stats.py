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
        fields = ["country", "survey_landscape__species", "survey_landscape__date", "survey_landscape__lsid"]


class SurveyStatsViewSet(StatsViewSet):
    serializer_class = SurveyStatsSerializer
    filter_class = SurveyStatsFilterSet
    queryset = SurveyStats.objects.select_related()
    ordering_fields = ["country", "survey_landscape__species", "survey_landscape__date", "survey_landscape__lsid"]

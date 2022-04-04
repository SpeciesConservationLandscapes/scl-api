from .base import BaseAPIFilterSet, LandscapeSerializer, StatsSerializer, StatsViewSet
from ..models import RestorationFragmentLandscape, RestorationFragmentStats, SpeciesFragmentLandscape, SpeciesFragmentStats, SurveyFragmentLandscape, SurveyFragmentStats


class RestorationFragmentSerializer(LandscapeSerializer):
    class Meta:
        model = RestorationFragmentLandscape
        exclude = []


class RestorationFragmentStatsSerializer(StatsSerializer):
    restoration_fragment = RestorationFragmentSerializer()

    class Meta(StatsSerializer.Meta):
        model = RestorationFragmentStats
        fields = ["id", "country", "restoration_fragment", "geom", "area", "biome_areas"]


class RestorationFragmentStatsFilterSet(BaseAPIFilterSet):
    class Meta(BaseAPIFilterSet.Meta):
        model = RestorationFragmentStats
        fields = ["country", "restoration_fragment__species", "restoration_fragment__date"]


class RestorationFragmentStatsViewSet(StatsViewSet):
    serializer_class = RestorationFragmentStatsSerializer
    filter_class = RestorationFragmentStatsFilterSet
    queryset = RestorationFragmentStats.objects.select_related()
    ordering_fields = ["country", "restoration_fragment__species", "restoration_fragment__date"]


class SpeciesFragmentSerializer(LandscapeSerializer):
    class Meta:
        model = SpeciesFragmentLandscape
        exclude = []


class SpeciesFragmentStatsSerializer(StatsSerializer):
    species_fragment = SpeciesFragmentSerializer()

    class Meta(StatsSerializer.Meta):
        model = SpeciesFragmentStats
        fields = ["id", "country", "species_fragment", "geom", "area", "biome_areas"]


class SpeciesFragmentStatsFilterSet(BaseAPIFilterSet):
    class Meta(BaseAPIFilterSet.Meta):
        model = SpeciesFragmentStats
        fields = ["country", "species_fragment__species", "species_fragment__date"]


class SpeciesFragmentStatsViewSet(StatsViewSet):
    serializer_class = SpeciesFragmentStatsSerializer
    filter_class = SpeciesFragmentStatsFilterSet
    queryset = SpeciesFragmentStats.objects.select_related()
    ordering_fields = ["country", "species_fragment__species", "species_fragment__date"]


class SurveyFragmentSerializer(LandscapeSerializer):
    class Meta:
        model = SurveyFragmentLandscape
        exclude = []


class SurveyFragmentStatsSerializer(StatsSerializer):
    survey_fragment = SurveyFragmentSerializer()

    class Meta(StatsSerializer.Meta):
        model = SurveyFragmentStats
        fields = ["id", "country", "survey_fragment", "geom", "area", "biome_areas"]


class SurveyFragmentStatsFilterSet(BaseAPIFilterSet):
    class Meta(BaseAPIFilterSet.Meta):
        model = SurveyFragmentStats
        fields = ["country", "survey_fragment__species", "survey_fragment__date"]


class SurveyFragmentStatsViewSet(StatsViewSet):
    serializer_class = SurveyFragmentStatsSerializer
    filter_class = SurveyFragmentStatsFilterSet
    queryset = SurveyFragmentStats.objects.select_related()
    ordering_fields = ["country", "survey_fragment__species", "survey_fragment__date"]

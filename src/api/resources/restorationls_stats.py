from .base import BaseAPIFilterSet, LandscapeSerializer, StatsSerializer, StatsViewSet
from ..models import RestorationLandscape, RestorationStats


class RestorationSerializer(LandscapeSerializer):
    class Meta:
        model = RestorationLandscape
        exclude = []


class RestorationStatsSerializer(StatsSerializer):
    restoration_landscape = RestorationSerializer()

    class Meta(StatsSerializer.Meta):
        model = RestorationStats
        fields = [
            "id",
            "country",
            "restoration_landscape",
            "geom",
            "area",
            "biome_areas",
        ]


class RestorationStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = RestorationStats
        fields = [
            "country",
            "restoration_landscape__species",
            "restoration_landscape__date",
            "restoration_landscape__lsid",
        ]


class RestorationStatsViewSet(StatsViewSet):
    serializer_class = RestorationStatsSerializer
    filter_class = RestorationStatsFilterSet
    queryset = RestorationStats.objects.select_related()
    ordering_fields = [
        "country",
        "restoration_landscape__species",
        "restoration_landscape__date",
        "restoration_landscape__lsid",
    ]

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
            "date",
            "restoration_landscape",
            "geom",
            "area",
            "biome_areas",
        ]


class RestorationStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = RestorationStats
        fields = ["country", "restoration_landscape__species", "date"]


class RestorationStatsViewSet(StatsViewSet):
    serializer_class = RestorationStatsSerializer
    filter_class = RestorationStatsFilterSet
    ordering_fields = ["country", "restoration_landscape__species", "date"]
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

        return RestorationStats.objects.filter(**filters).select_related()

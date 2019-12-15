from .base import BaseAPIFilterSet, LandscapeSerializer, StatsSerializer, StatsViewSet
from ..models import FragmentLandscape, FragmentStats


class FragmentSerializer(LandscapeSerializer):
    class Meta:
        model = FragmentLandscape
        exclude = []


class FragmentStatsSerializer(StatsSerializer):
    fragment = FragmentSerializer()

    class Meta(StatsSerializer.Meta):
        model = FragmentStats
        fields = ["id", "country", "fragment", "geom", "area", "biome_areas"]


class FragmentStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = FragmentStats
        fields = ["country", "fragment__species", "fragment__date"]


class FragmentStatsViewSet(StatsViewSet):
    serializer_class = FragmentStatsSerializer
    filter_class = FragmentStatsFilterSet
    ordering_fields = ["country", "fragment__species", "fragment__date"]
    required_filters = ["country", "fragment__species", "fragment__date"]

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
            "fragment__date": self.request.query_params["fragment__date"],
        }

        return FragmentStats.objects.filter(**filters).select_related()

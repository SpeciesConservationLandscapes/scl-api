from rest_framework_gis.pagination import GeoJsonPagination
from .base import BaseAPIFilterSet, BaseAPIViewSet, LandscapeSerializer, StatsSerializer
from ..models import FragmentLandscape, FragmentStats


class FragmentSerializer(LandscapeSerializer):
    class Meta:
        model = FragmentLandscape
        exclude = []


class FragmentStatsSerializer(StatsSerializer):
    fragment = FragmentSerializer()

    class Meta(StatsSerializer.Meta):
        model = FragmentStats
        fields = ["id", "country", "date", "fragment", "geom", "areas"]


class FragmentStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = FragmentStats
        fields = ["country", "fragment__species", "date"]


class FragmentStatsViewSet(BaseAPIViewSet):
    pagination_class = GeoJsonPagination
    serializer_class = FragmentStatsSerializer
    filter_class = FragmentStatsFilterSet
    ordering_fields = ["country", "fragment__species", "date"]
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

        return FragmentStats.objects.filter(**filters).select_related()

from rest_framework import serializers
from .base import BaseAPIFilterSet, StatsSerializer, StatsViewSet
from ..models import IndigenousRangeCountryStats


class IndigenousRangeStatsSerializer(StatsSerializer):
    species = serializers.SerializerMethodField()

    class Meta(StatsSerializer.Meta):
        model = IndigenousRangeCountryStats
        exclude = []

    @staticmethod
    def get_species(obj):
        return str(obj.species)


class IndigenousRangeStatsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = IndigenousRangeCountryStats
        fields = ["country", "species"]


class IndigenousRangeStatsViewSet(StatsViewSet):
    serializer_class = IndigenousRangeStatsSerializer
    filter_class = IndigenousRangeStatsFilterSet
    queryset = IndigenousRangeCountryStats.objects.select_related()
    ordering_fields = ["species", "country"]

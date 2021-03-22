from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .base import BaseAPISerializer, BaseAPIFilterSet, BaseAPIViewSet, StandardResultPagination
from observations.models import Record


class RecordsSerializer(GeoFeatureModelSerializer, BaseAPISerializer):

    class Meta:
        model = Record
        fields = "__all__"
        geo_field = "point"


class RecordsFilterSet(BaseAPIFilterSet):
    class Meta:
        model = Record
        fields = ["id", "year", "sex", "age", "date_type", "locality_type", "observation_type"]


class RecordsViewSet(BaseAPIViewSet):
    authentication_classes = []
    permission_classes = []
    pagination_class = StandardResultPagination
    serializer_class = RecordsSerializer
    filter_class = RecordsFilterSet

    def get_queryset(self):
        return Record.objects.filter(canonical=True).select_related()


from rest_framework import serializers
from .base import BaseAPISerializer, BaseAPIFilterSet, BaseAPIViewSet
from ..models import Species, SCLStats


class SpeciesSerializer(BaseAPISerializer):
    scientific_name = serializers.SerializerMethodField()
    countries = serializers.SerializerMethodField()

    class Meta:
        model = Species
        fields = [
            "id",
            "scientific_name",
            "name_common",
            "genus",
            "name",
            "colid",
            "iucnid",
            "notes",
            "countries",
        ]

    @staticmethod
    def get_scientific_name(obj):
        return str(obj)

    def get_countries(self, obj):
        request = self.context.get("request")
        filters = {"scl__species": obj}
        if (
            request
            and hasattr(request, "query_params")
            and "date" in request.query_params
            and request.query_params["date"] != ""
        ):
            filters["date"] = request.query_params["date"]
        qs = SCLStats.objects.filter(**filters)
        return (
            qs.order_by("country").distinct("country").values_list("country", flat=True)
        )


class SpeciesFilterSet(BaseAPIFilterSet):
    class Meta:
        model = Species
        fields = ["genus__name", "name", "name_common", "colid", "iucnid"]


class SpeciesViewSet(BaseAPIViewSet):
    serializer_class = SpeciesSerializer
    filter_class = SpeciesFilterSet
    ordering_fields = ["id", "genus__name", "name", "name_common", "colid", "iucnid"]

    def get_queryset(self):
        return Species.objects.select_related()

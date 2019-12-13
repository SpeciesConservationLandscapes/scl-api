from rest_framework import serializers, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import BasePermission
import django_filters
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.filterset import GeoFilterSet
from django_countries.serializer_fields import CountryField


META_FIELDS = ["created_on", "created_by", "updated_on", "updated_by"]


class BaseExcludedFieldsMixin(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = self.get_fields()
        for field in fields:
            if field in META_FIELDS:
                self.fields.pop(field)


class BaseAPISerializer(BaseExcludedFieldsMixin, serializers.ModelSerializer):
    pass


class LandscapeSerializer(BaseExcludedFieldsMixin, serializers.ModelSerializer):
    species = serializers.SerializerMethodField()

    @staticmethod
    def get_species(obj):
        return str(obj.species)


class StatsSerializer(BaseExcludedFieldsMixin, GeoFeatureModelSerializer):
    country = CountryField(country_dict=True)
    geom = GeometryField(precision=4, remove_duplicates=True)
    areas = serializers.JSONField()

    class Meta:
        geo_field = "geom"


class BaseAPIFilterSet(GeoFilterSet):
    id = django_filters.NumberFilter()
    created_on = django_filters.DateTimeFromToRangeFilter()
    created_by = django_filters.NumberFilter()
    updated_on = django_filters.DateTimeFromToRangeFilter()
    updated_by = django_filters.NumberFilter()

    class Meta:
        fields = ["id"] + META_FIELDS


class StandardResultPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "limit"
    max_page_size = 5000


class UserCountryPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        query = request.query_params
        if not user.is_authenticated or "country" not in query:
            return False

        return query["country"] in user.profile.countries


class BaseAPIViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultPagination

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed("POST")

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH")

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE")


class StatsViewSet(BaseAPIViewSet):
    pagination_class = GeoJsonPagination
    permission_classes = [UserCountryPermission]

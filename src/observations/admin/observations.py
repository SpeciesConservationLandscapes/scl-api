import copy
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.contrib.gis import admin
from django.contrib.gis.geos import Point
from .base import *
from observations.models import *


@admin.register(DateType)
class DateTypeAdmin(TypeAdmin):
    pass


@admin.register(LocalityType)
class LocalityTypeAdmin(TypeAdmin):
    pass


@admin.register(ObsProfile)
class ObsProfileAdmin(BaseAdmin):
    pass


@admin.register(ObservationTypeGroup)
class ObservationTypeGroupAdmin(BaseObservationAdmin):
    fields = ["name", ("created_by", "created_on"), ("updated_by", "updated_on")]


@admin.register(ObservationType)
class ObservationTypeAdmin(TypeAdmin):
    list_display = [
        "sequence",
        "name",
        "description",
        "examples",
        "observation_type_group",
    ]
    fields = [
        "sequence",
        "name",
        "description",
        "examples",
        "observation_type_group",
        ("created_by", "created_on"),
        ("updated_by", "updated_on"),
    ]


@admin.register(Reference)
class ReferenceAdmin(BaseObservationAdmin):
    list_display = ["name_short", "year", zotero_link, "updated_on"]
    list_filter = ["year", "created_by", "updated_by"]
    search_fields = ["name", "name_short", "year", "zotero"]
    fields = [
        "name",
        "name_short",
        "year",
        "zotero",
        "description",
        ("created_by", "created_on"),
        ("updated_by", "updated_on"),
    ]


class RecordInlineFormset(CanonicalInlineFormset):
    atleast_one = True


class RecordInline(admin.StackedInline, BaseObservationAdmin):
    model = Record
    fields = [
        ("canonical", "year"),
        "point",
        ("reference", "page_numbers"),
        ("locality_type", "locality_text"),
        ("date_type", "date_text"),
        ("observation_type", "observation_text"),
        ("sex", "age"),
        "notes",
        ("created_by", "created_on"),
        ("updated_by", "updated_on"),
    ]
    min_num = 1
    extra = 0
    formset = RecordInlineFormset

    # TODO: find better map solution -- everything below here is for inline maps
    map_width = 800
    pnt = Point(90, 27, srid=4326)
    pnt.transform(3857)
    default_lon, default_lat = pnt.coords
    display_srid = 4326
    point_zoom = 5

    def __init__(self, parent_model, admin_site):
        self.admin_site = admin_site
        self.parent_model = parent_model
        self.opts = self.model._meta
        self.has_registered_model = admin_site.is_registered(self.model)
        overrides = copy.deepcopy(FORMFIELD_FOR_DBFIELD_DEFAULTS)
        for k, v in self.formfield_overrides.items():
            overrides.setdefault(k, {}).update(v)
        self.formfield_overrides = overrides
        if self.verbose_name is None:
            self.verbose_name = self.model._meta.verbose_name
        if self.verbose_name_plural is None:
            self.verbose_name_plural = self.model._meta.verbose_name_plural


@admin.register(Observation)
class ObservationAdmin(BaseObservationAdmin):
    # TODO: change export_model_all_as_csv or otherwise export canonical record fields
    list_display = [
        "id",
        "year",
        "reference",
        "date_type",
        "locality_type",
        "observation_type",
        "latitude",
        "longitude",
        "updated_on",
    ]
    # TODO: add "year", "date_type", "locality_type", "observation_type" via custom filters
    list_filter = ["created_by", "updated_by"]
    search_fields = ("id", "year", "reference")
    fields = [
        "species",
        "notes",
        ("created_by", "created_on"),
        ("updated_by", "updated_on"),
    ]
    inlines = [RecordInline]

    def year(self, obj):
        return obj.year

    year.admin_order_field = "year"

    def latitude(self, obj):
        return obj.point.y

    def longitude(self, obj):
        return obj.point.x

    def reference(self, obj):
        return obj.reference

    reference.admin_order_field = "reference"

    # def reference_link(self, obj):
    #     return zotero_link(obj, False)
    #
    # reference_link.admin_order_field = "reference"

    def date_type(self, obj):
        return obj.date_type

    date_type.admin_order_field = "date_type"

    def locality_type(self, obj):
        return obj.locality_type

    locality_type.admin_order_field = "locality_type"

    def observation_type(self, obj):
        return obj.observation_type

    observation_type.admin_order_field = "observation_type"

import copy
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.contrib.gis import admin
from django.contrib.gis.geos import Point
from .base import *
from observations.models import *


def year(obj):
    return obj.year


def latitude(obj):
    y = ""
    if obj.point and hasattr(obj.point, "y"):
        y = str(obj.point.y)
    return y


def longitude(obj):
    x = ""
    if obj.point and hasattr(obj.point, "x"):
        x = str(obj.point.x)
    return x


def reference(obj):
    return obj.reference


# def reference_link(self, obj):
#     return zotero_link(obj, False)
#
# reference_link.admin_order_field = "reference"


def date_type(obj):
    return obj.date_type


def locality_type(obj):
    return obj.locality_type


def observation_type(obj):
    return obj.observation_type


year.admin_order_field = "year"
reference.admin_order_field = "reference"
date_type.admin_order_field = "date_type"
locality_type.admin_order_field = "locality_type"
observation_type.admin_order_field = "observation_type"

record_fields = [
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

record_list_display = [
    year,
    reference,
    date_type,
    locality_type,
    observation_type,
    latitude,
    longitude,
    "updated_on",
]


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


@admin.register(Record)
class RecordAdmin(BaseObservationAdmin):
    list_display = ["selfstr", "canonical"] + record_list_display + ["observation"]
    list_filter = [
        "canonical",
        "date_type",
        "locality_type",
        "observation_type",
        "created_by",
        "updated_by",
    ]
    search_fields = ("id", "year", "reference__name", "sex", "age")
    fields = ["observation"] + record_fields

    def selfstr(self, obj):
        return obj.__str__()

    selfstr.short_description = "record"

    map_width = 800
    pnt = Point(90, 27, srid=4326)
    pnt.transform(3857)
    default_lon, default_lat = pnt.coords
    display_srid = 4326
    point_zoom = 5

    # disable deleting selected for records, but preserve individual deletion and csv export
    def get_actions(self, request):
        actions = super(RecordAdmin, self).get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def delete_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)

        parent, siblings, canonical_siblings = obj.get_family()
        try:
            check_siblings(obj, parent, siblings, canonical_siblings, True)
        except ValidationError as e:
            error_dict = dict(e)
            error = "Cannot delete this canonical record until another record for this observation is canonical."
            if "canonical" in error_dict:
                error = error_dict["canonical"]
                if isinstance(error, list):
                    error = "<br />".join(error)
            extra_context["title"] = "Delete disallowed"
            extra_context["non_canonical_siblings"] = error

        return super().delete_view(request, object_id, extra_context=extra_context)


class RecordInlineFormset(CanonicalInlineFormset):
    atleast_one = True


class RecordInline(admin.StackedInline, BaseObservationAdmin):
    model = Record
    fields = record_fields
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
    list_display = ["selfstr"] + record_list_display
    # TODO: add "date_type", "locality_type", "observation_type" via custom filters
    list_filter = ["created_by", "updated_by"]
    search_fields = ("id", "year", "reference")
    fields = [
        "species",
        "notes",
        ("created_by", "created_on"),
        ("updated_by", "updated_on"),
    ]
    inlines = [RecordInline]

    def selfstr(self, obj):
        return obj.__str__()

    selfstr.short_description = "observation"

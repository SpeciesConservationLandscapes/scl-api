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


@admin.register(ObservationTypeGroup)
class ObservationTypeGroupAdmin(BaseObservationAdmin):
    fields = [
        "name",
        ("created_by", "created_on"),
        ("updated_by", "updated_on"),
    ]


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
    list_filter = ["created_by", "updated_by", "year"]
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

    # def __init__(self, data=None, files=None, instance=None,
    #              save_as_new=False, prefix=None, queryset=None, **kwargs):
    #     self.atleast_one = True
    #     super().__init__(data=None, files=None, instance=None,
    #                      save_as_new=False, prefix=None, queryset=None, **kwargs)
    #     print(f"RecordInlineFormset init atleast_one: {self.atleast_one}")

    # def clean(self):
    #     self.atleast_one = True
    #     print(f"RecordInlineFormset clean atleast_one: {self.atleast_one}")
    #     super().clean()


class RecordInline(admin.StackedInline, BaseObservationAdmin):
    model = Record
    fields = [
        ("canonical", "year"),
        "point",
        ("reference", "page_numbers"),
        "locality_type",
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
    # list_display = []
    # list_filter = []
    # search_fields = ()
    fields = [
        "species",
        "notes",
        ("created_by", "created_on"),
        ("updated_by", "updated_on"),
    ]
    inlines = [RecordInline, ]

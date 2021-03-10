from django.contrib import admin
from django.db.models import Max
from django.forms import TextInput
from django.utils.html import format_html
from api.admin import BaseAdmin
from .models import *


def zotero_link(obj):
    return format_html(
        f'<a href="https://www.zotero.org/groups/{settings.ZOTERO_GROUP}/items/itemKey/{obj.zotero}" target="_blank">'
        f'{obj.zotero}</a>'
    )
zotero_link.admin_order_field = "zotero"


class BaseObservationAdmin(BaseAdmin):
    readonly_fields = ["created_by", "created_on", "updated_by", "updated_on"]
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "100%"})}
    }

    def save_model(self, request, obj, form, change):
        profile = request.user.profile
        if change:
            obj.created_by = profile
        obj.updated_by = profile
        super().save_model(request, obj, form, change)


class TypeAdmin(BaseObservationAdmin):
    list_display = ["sequence", "name", "description", "examples"]
    list_display_links = ["sequence", "name"]
    fields = [
        "sequence",
        "name",
        "description",
        "examples",
        ("created_by", "created_on"),
        ("updated_by", "updated_on"),
    ]

    def get_changeform_initial_data(self, request):
        max_sequence = (
            self.model.objects.aggregate(Max("sequence"))["sequence__max"] or 0
        )
        return {"sequence": max_sequence + 1}


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


@admin.register(Observation)
class ObservationAdmin(BaseObservationAdmin):
    pass


@admin.register(Record)
class RecordAdmin(BaseObservationAdmin):
    pass

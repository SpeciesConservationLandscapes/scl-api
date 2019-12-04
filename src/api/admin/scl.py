from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from .base import BaseAdmin
from ..models.scl import *


linkstr = '<a href="{}{}{}" target="_blank">{}</a>'


@admin.register(Genus)
class GenusAdmin(BaseAdmin):
    pass


@admin.register(Species)
class SpeciesAdmin(BaseAdmin):
    list_display = ("full_name", "name_common", "col_link", "iucn_link")

    def col_link(self, obj):
        root = "https://www.catalogueoflife.org/col/details/species/id/"
        return format_html(linkstr, root, obj.colid, "", obj.colid)

    col_link.short_description = _("Catalog Of Life ID")

    def iucn_link(self, obj):
        root = "http://apiv3.iucnredlist.org/api/v3/species/id/"
        # temporary, from example; seems to not expire
        token = "9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee"
        return format_html(
            linkstr, root, obj.iucnid, "?token={}".format(token), obj.iucnid
        )

    iucn_link.short_description = _("IUCN ID")


@admin.register(Biome)
class BiomeAdmin(BaseAdmin):
    list_display = ("name", "biomeid")


@admin.register(ProtectedArea)
class ProtectedAreaAdmin(BaseAdmin):
    list_display = ("name", "wdpa_link")

    def wdpa_link(self, obj):
        root = "http://www.protectedplanet.net/"
        return format_html(linkstr, root, obj.wdpaid, "", obj.wdpaid)

    wdpa_link.short_description = _("WDPA ID")


@admin.register(SCL)
class SCLAdmin(BaseAdmin):
    list_display = ("name", "sclclass")


@admin.register(FragmentLandscape)
class FragmentLandscapeAdmin(BaseAdmin):
    pass


@admin.register(RestorationLandscape)
class RestorationLandscapeAdmin(BaseAdmin):
    pass


@admin.register(SurveyLandscape)
class SurveyLandscapeAdmin(BaseAdmin):
    pass


@admin.register(SCLStats)
class SCLStatsAdmin(BaseAdmin):
    list_display = ("scl", "country", "biome", "pa", "date")


@admin.register(FragmentStats)
class FragmentStatsAdmin(BaseAdmin):
    list_display = ("fragment", "country", "biome", "pa", "date")


@admin.register(RestorationStats)
class RestorationStatsAdmin(BaseAdmin):
    list_display = ("restoration_landscape", "country", "biome", "pa", "date")


@admin.register(SurveyStats)
class SurveyStatsAdmin(BaseAdmin):
    list_display = ("survey_landscape", "country", "biome", "pa", "date")

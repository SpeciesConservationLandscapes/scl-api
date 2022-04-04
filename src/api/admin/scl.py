from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from .base import BaseAdmin, StatsAdmin
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


@admin.register(SCL)
class SCLAdmin(BaseAdmin):
    list_display = ("lsid", "name", "species", "date")


@admin.register(RestorationLandscape)
class RestorationLandscapeAdmin(BaseAdmin):
    pass


@admin.register(SurveyLandscape)
class SurveyLandscapeAdmin(BaseAdmin):
    pass


@admin.register(SpeciesFragmentLandscape)
class SpeciesFragmentLandscapeAdmin(BaseAdmin):
    pass


@admin.register(RestorationFragmentLandscape)
class RestorationFragmentLandscapeAdmin(BaseAdmin):
    pass


@admin.register(SurveyFragmentLandscape)
class SurveyFragmentLandscapeAdmin(BaseAdmin):
    pass


@admin.register(SCLStats)
class SCLStatsAdmin(StatsAdmin):
    landscape_key = "scl"


@admin.register(RestorationStats)
class RestorationStatsAdmin(StatsAdmin):
    landscape_key = "restoration_landscape"


@admin.register(SurveyStats)
class SurveyStatsAdmin(StatsAdmin):
    landscape_key = "survey_landscape"


@admin.register(SpeciesFragmentStats)
class SpeciesFragmentStatsAdmin(StatsAdmin):
    landscape_key = "species_fragment"


@admin.register(RestorationFragmentStats)
class RestorationFragmentStatsAdmin(StatsAdmin):
    landscape_key = "restoration_fragment"


@admin.register(SurveyFragmentStats)
class SurveyFragmentStatsAdmin(StatsAdmin):
    landscape_key = "survey_fragment"


@admin.register(IndigenousRangeCountryStats)
class IndigenousRangeCountryStatsAdmin(BaseAdmin):
    list_display = ("species", "country", "area",)
    list_filter = ("species", "country",)

from decimal import Decimal
from django.conf import settings
from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django_countries.fields import CountryField
from .base import BaseModel


class Genus(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = _("genera")

    def __str__(self):
        return _("%s") % self.name


class Species(BaseModel):
    name = models.CharField(max_length=100)
    genus = models.ForeignKey(Genus, on_delete=models.CASCADE)
    name_common = models.CharField(
        max_length=255, blank=True, verbose_name=_("common name (English)")
    )
    # https://www.catalogueoflife.org/col/details/species/id/9c35aba4cb7f388bf29a05fba221135c
    colid = models.CharField(
        max_length=32, verbose_name=_("Catalog of Life ID"), unique=True
    )
    # http://apiv3.iucnredlist.org/api/v3/species/id/15955?token
    # =9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee
    iucnid = models.PositiveIntegerField(verbose_name=_("IUCN ID"), unique=True)
    notes = models.TextField(blank=True)

    @property
    def ee_path(self):
        if settings.EE_SCL_ROOTDIR is None:
            return None
        return "{}/{}_{}/aoi".format(
            settings.EE_SCL_ROOTDIR, self.genus.name.capitalize(), self.name
        )

    @property
    def full_name(self):
        return _("%s %s") % (self.genus.name.capitalize(), self.name)

    class Meta:
        ordering = ("genus", "name")
        verbose_name_plural = _("species")

    def __str__(self):
        return self.full_name


class Landscape(BaseModel):
    ee_name = None

    lsid = models.PositiveIntegerField(verbose_name=_("landscape ID"))
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    @property
    def ee_path(self):
        if settings.EE_SCL_ROOTDIR is None or self.ee_name is None:
            return None
        return "{}/{}_{}/{}".format(
            settings.EE_SCL_ROOTDIR,
            self.species.genus.name.capitalize(),
            self.species.name,
            self.ee_name,
        )

    class Meta:
        abstract = True
        ordering = ("name", "species")

    def __str__(self):
        if settings.EE_SCL_ROOTDIR is None or self.ee_name is None:
            return ""
        name = ""
        if hasattr(self, "name"):
            name = " {}".format(self.name)
        return _("%s %s%s %s [%s]") % (self.ee_name, self.lsid, name, self.species, self.date)


class SCL(Landscape):
    ee_name = "scl"

    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("species conservation landscape")
        verbose_name_plural = _("species conservation landscapes")


class RestorationLandscape(Landscape):
    ee_name = "restoration"

    class Meta:
        verbose_name = _("restoration landscape")
        verbose_name_plural = _("restoration landscapes")


class SurveyLandscape(Landscape):
    ee_name = "survey"

    class Meta:
        verbose_name = _("survey landscape")
        verbose_name_plural = _("survey landscapes")


class SpeciesFragmentLandscape(Landscape):
    ee_name = "species_fragment"

    class Meta:
        verbose_name = _("species conservation landscape fragment")
        verbose_name_plural = _("species conservation landscape fragments")


class RestorationFragmentLandscape(Landscape):
    ee_name = "restoration_fragment"

    class Meta:
        verbose_name = _("restoration landscape fragment")
        verbose_name_plural = _("restoration landscape fragments")


class SurveyFragmentLandscape(Landscape):
    ee_name = "survey_fragment"

    class Meta:
        verbose_name = _("survey landscape fragment")
        verbose_name_plural = _("survey landscape fragments")


class LandscapeCountryStats(BaseModel):
    country = CountryField()
    geom = models.MultiPolygonField(geography=True, null=True, blank=True)
    area = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal("0.00"))
    biome_areas = JSONField(null=True, blank=True)

    class Meta:
        abstract = True


class SCLStats(LandscapeCountryStats):
    scl = models.ForeignKey(SCL, on_delete=models.CASCADE)

    class Meta:
        ordering = ("country", "scl__date")
        verbose_name = _("SCL statistics")
        verbose_name_plural = _("SCL statistics")

    def __str__(self):
        return _("%s %s") % (self.scl, self.country)


class RestorationStats(LandscapeCountryStats):
    restoration_landscape = models.ForeignKey(
        RestorationLandscape, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("country", "restoration_landscape__date")
        verbose_name = _("restoration landscape statistics")
        verbose_name_plural = _("restoration landscape statistics")

    def __str__(self):
        return _("%s %s") % (self.restoration_landscape, self.country)


class SurveyStats(LandscapeCountryStats):
    survey_landscape = models.ForeignKey(SurveyLandscape, on_delete=models.CASCADE)

    class Meta:
        ordering = ("country", "survey_landscape__date")
        verbose_name = _("survey landscape statistics")
        verbose_name_plural = _("survey landscape statistics")

    def __str__(self):
        return _("%s %s") % (self.survey_landscape, self.country)


class SpeciesFragmentStats(LandscapeCountryStats):
    species_fragment = models.ForeignKey(SpeciesFragmentLandscape, on_delete=models.CASCADE)

    class Meta:
        ordering = ("country", "species_fragment__date")
        verbose_name = _("species fragment statistics")
        verbose_name_plural = _("species fragment statistics")

    def __str__(self):
        return _("%s %s") % (self.species_fragment, self.country)


class RestorationFragmentStats(LandscapeCountryStats):
    restoration_fragment = models.ForeignKey(RestorationFragmentLandscape, on_delete=models.CASCADE)

    class Meta:
        ordering = ("country", "restoration_fragment__date")
        verbose_name = _("restoration fragment statistics")
        verbose_name_plural = _("restoration fragment statistics")

    def __str__(self):
        return _("%s %s") % (self.restoration_fragment, self.country)


class SurveyFragmentStats(LandscapeCountryStats):
    survey_fragment = models.ForeignKey(SurveyFragmentLandscape, on_delete=models.CASCADE)

    class Meta:
        ordering = ("country", "survey_fragment__date")
        verbose_name = _("survey fragment statistics")
        verbose_name_plural = _("survey fragment statistics")

    def __str__(self):
        return _("%s %s") % (self.survey_fragment, self.country)


class IndigenousRangeCountryStats(BaseModel):
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    country = CountryField()
    geom = models.MultiPolygonField(geography=True, null=True, blank=True)
    area = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ("species", "country")

    def __str__(self):
        return _("%s %s") % (self.species, self.country)

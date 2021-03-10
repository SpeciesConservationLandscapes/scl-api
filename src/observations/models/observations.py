from django.utils.translation import ugettext as _
from .base import *
from api.models import Species


class DateType(TypeModel):
    pass


class LocalityType(TypeModel):
    pass


class ObservationTypeGroup(BaseModel):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return _(self.name)


class ObservationType(TypeModel):
    observation_type_group = models.ForeignKey(ObservationTypeGroup, on_delete=models.CASCADE)


class Reference(BaseModel):
    name = models.CharField(max_length=255, verbose_name="reference")
    name_short = models.CharField(max_length=100, verbose_name="short name")
    year = models.SmallIntegerField(blank=True, null=True)
    zotero = models.CharField(max_length=8, verbose_name="zotero ID")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name_short"]

    def __str__(self):
        return _(f"{self.name_short}")


class Observation(BaseModel):
    species = models.ForeignKey(Species, default=default_species, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.pk


class Record(CanonicalModel):
    UNKNOWN = "unknown"
    SEX_CHOICES = (("male", "male"), ("female", "female"), (UNKNOWN, UNKNOWN))
    AGE_CHOICES = (("mature", "mature"), ("immature", "immature"), (UNKNOWN, UNKNOWN))
    parent = Observation

    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    reference = models.ForeignKey(Reference, on_delete=models.PROTECT)
    page_numbers = models.CharField(max_length=50, blank=True)
    year = models.SmallIntegerField(blank=True, null=True)
    date_type = models.ForeignKey(DateType, on_delete=models.PROTECT)
    date_text = models.TextField(blank=True)
    locality_type = models.ForeignKey(LocalityType, on_delete=models.PROTECT)
    sex = models.CharField(max_length=50, choices=SEX_CHOICES)
    age = models.CharField(max_length=50, choices=AGE_CHOICES)
    observation_type = models.ForeignKey(ObservationType, on_delete=models.PROTECT)
    observation_text = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    point = models.PointField(geography=True, blank=True, null=True)

    class Meta:
        ordering = ["observation__pk"]

    def __str__(self):
        year = f" {str(self.year)}" or ""
        return f"[{self.observation}]{year} {self.reference.name_short}"

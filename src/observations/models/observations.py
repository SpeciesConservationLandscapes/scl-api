from django.db.models import F
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
    observation_type_group = models.ForeignKey(
        ObservationTypeGroup, on_delete=models.CASCADE
    )


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


class ObservationManager(models.Manager):
    def get_queryset(self):
        record_fields = {}
        base_fields = [f.name for f in BaseModel._meta.fields] + ["notes"]
        for field in Record._meta.get_fields(include_parents=False):
            if (
                field.concrete
                and not field.hidden
                and not field.primary_key
                and field.name not in base_fields
            ):
                lookup = f"record__{field.name}"
                if field.is_relation:
                    if issubclass(field.related_model, TypeModel):
                        lookup = f"record__{field.name}__name"
                    elif field.name == "reference":
                        lookup = "record__reference__name_short"
                record_fields[field.name] = F(lookup)
        record_fields["zotero"] = F("record__reference__zotero")

        qs = (
            super()
            .get_queryset()
            .prefetch_related("record_set")
            .filter(record__canonical=True)
            .annotate(**record_fields)
        )
        return qs


class Observation(BaseModel):
    species = models.ForeignKey(
        Species, default=default_species, on_delete=models.PROTECT
    )
    notes = models.TextField(blank=True)

    objects = ObservationManager()

    def __str__(self):
        notes = self.notes
        if len(notes) > 0:
            shortened_notes = f" {notes[:20]}"
            if len(shortened_notes) > 20:
                shortened_notes = f"{shortened_notes}..."
            notes = shortened_notes
        return f"{str(self.pk)}{notes}"


class Record(CanonicalModel):
    UNKNOWN = "unknown"
    SEX_CHOICES = (("male", "male"), ("male - uncertain", "male - uncertain"),
                   ("female", "female"), ("female - uncertain", "female - uncertain"),
                   (UNKNOWN, UNKNOWN)
                   )
    AGE_CHOICES = (("adult", "adult"), ("adult - uncertain", "adult - uncertain"),
                   ("immature", "immature"), ("immature - uncertain", "immature - uncertain"),
                   (UNKNOWN, UNKNOWN)
                   )
    parent = Observation

    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    reference = models.ForeignKey(Reference, on_delete=models.PROTECT)
    page_numbers = models.CharField(max_length=50, blank=True)
    year = models.SmallIntegerField(blank=True, null=True)
    date_type = models.ForeignKey(DateType, on_delete=models.PROTECT)
    date_text = models.TextField(blank=True)
    locality_type = models.ForeignKey(LocalityType, on_delete=models.PROTECT)
    locality_text = models.TextField(blank=True)
    sex = models.CharField(max_length=50, choices=SEX_CHOICES, default=UNKNOWN)
    age = models.CharField(max_length=50, choices=AGE_CHOICES, default=UNKNOWN)
    observation_type = models.ForeignKey(ObservationType, on_delete=models.PROTECT)
    observation_text = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    point = models.PointField(srid=4326, blank=True, null=True)

    class Meta:
        ordering = ["observation_id", "-canonical", "year", "reference__name_short"]

    def __str__(self):
        year = ""
        if self.year:
            year = f" {str(self.year)}"
        return f"[{self.observation}]{year} {self.reference.name_short}"

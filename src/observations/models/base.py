from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from api.models import Species


def default_species():
    return Species.objects.get(genus__name="Panthera", name="tigris").pk


def make_single_sibling_canonical(siblings, canonical_siblings):
    if siblings.count() == 1 and canonical_siblings.count() < 1:
        single_sibling = siblings[0]
        single_sibling.canonical = True
        single_sibling.save_simple()


def check_siblings(instance, parent, siblings, canonical_siblings, deleting=False):
    canonical_flag = False
    if (instance.canonical and deleting) or (not instance.canonical and not deleting):
        canonical_flag = True
    sibling_count = siblings.count()
    if (sibling_count < 1 and deleting) or (
        canonical_flag and sibling_count > 1 and canonical_siblings.count() < 1
    ):
        link = reverse(
            "admin:%s_%s_change" % (parent._meta.app_label, parent._meta.model_name),
            args=(parent.pk,),
        )
        raise ValidationError(
            {
                NON_FIELD_ERRORS: mark_safe(
                    f"You may not delete or deselect {instance} as canonical, or reassign to another "
                    f"{parent._meta.model_name}, until you mark another "
                    f"{instance._meta.model_name} for <a href={link}>{parent._meta.model_name} "
                    f"{parent}</a> as canonical."
                )
            }
        )


class ObsProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "observations user profile"

    def __str__(self):
        name = self.user.get_full_name()
        if name is None or name == "":
            name = self.user
        return str(name)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    profile, created = ObsProfile.objects.get_or_create(user=instance)
    profile.save()


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "observations.ObsProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
    )
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "observations.ObsProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
    )

    class Meta:
        abstract = True


class CanonicalModel(BaseModel):
    canonical = models.BooleanField(default=False)
    _existing_family = None

    @property
    def parent(self):
        raise NotImplementedError(
            "Inheritors of CanonicalModel must provide a parent attribute"
        )

    @property
    def existing_family(self):
        if not self._existing_family:
            try:
                old_instance = type(self).objects.get(pk=self.pk)
                old_parent, old_siblings, old_canonical_siblings = (
                    old_instance.get_family()
                )
                self._existing_family = (
                    old_instance,
                    old_parent,
                    old_siblings,
                    old_canonical_siblings,
                )
            except type(self).DoesNotExist:
                pass  # creating new instance
        return self._existing_family

    def get_family(self):
        parent = getattr(self, self.parent._meta.model_name)
        kwargs = {f"{parent._meta.model_name}__exact": parent.pk}
        siblings = type(self).objects.filter(**kwargs).exclude(pk=self.pk)
        canonical_siblings = siblings.filter(canonical=True)
        return parent, siblings, canonical_siblings

    def ensure_canonical(self, parent, siblings, canonical_siblings):
        # If there are no other objects for this parent, make sure this one is canonical
        if siblings.count() == 0:
            self.canonical = True
        # if obj is canonical, make any siblings not
        if self.canonical:
            for other in siblings:
                other.canonical = False
                other.save_simple()
        # if adding/saving as noncanonical, make sure something else is canonical
        else:
            make_single_sibling_canonical(siblings, canonical_siblings)
            check_siblings(self, parent, siblings, canonical_siblings)

    def pre_transfer_check(self):
        parent = getattr(self, self.parent._meta.model_name)
        # check old family if transferring, as if deleting
        if self.existing_family and self.existing_family[1].pk != parent.pk:
            check_siblings(
                self.existing_family[0],
                self.existing_family[1],
                self.existing_family[2],
                self.existing_family[3],
                True,
            )

    def clean(self):
        parent, siblings, canonical_siblings = self.get_family()
        self.pre_transfer_check()
        check_siblings(self, parent, siblings, canonical_siblings)

    def save(self, *args, **kwargs):
        parent, siblings, canonical_siblings = self.get_family()
        self.pre_transfer_check()
        self.ensure_canonical(parent, siblings, canonical_siblings)
        if self.existing_family and self.existing_family[1].pk != parent.pk:
            make_single_sibling_canonical(
                self.existing_family[2], self.existing_family[3]
            )
        super().save(*args, **kwargs)

    def save_simple(self, *args, **kwargs):
        print(self.__dict__)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        parent, siblings, canonical_siblings = self.get_family()
        make_single_sibling_canonical(siblings, canonical_siblings)
        check_siblings(self, parent, siblings, canonical_siblings, True)
        super().delete(*args, **kwargs)

    class Meta:
        abstract = True


class TypeModel(BaseModel):
    sequence = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    examples = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True
        ordering = ["sequence", "name"]

    def __str__(self):
        return _(self.name)

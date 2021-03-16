from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from api.models import Species


def default_species():
    return Species.objects.get(genus__name="Panthera", name="tigris").pk


def ensure_canonical(instance, parent, siblings, *args):
    othercan = 0
    # If there are no other objects for this parent, make sure this one is canonical, and then just return
    if siblings.count() == 0:
        instance.canonical = True
        # ? instance.save()
    # if operation is add/save and obj is canonical, make all others not
    elif instance.canonical and "delete" not in args:
        for other in siblings:
            other.canonical = False
            other.save_simple()
    # if adding/saving as noncanonical OR deleting (canonical or not), make sure something else is canonical
    elif not instance.canonical or "delete" in args:
        for other in siblings:
            if other.canonical:
                othercan += 1
        if othercan < 1:
            # If there's only one other object for this parent, set it as canonical
            if siblings.count() == 1:
                siblings[0].canonical = True
                siblings[0].save_simple()
            else:
                # Otherwise, make the user choose another object as canonical
                link = reverse(
                    "admin:%s_%s_change"
                    % (parent._meta.app_label, parent._meta.model_name),
                    args=(parent.pk,),
                    )
                raise ValidationError(
                    {
                        "canonical": mark_safe(
                            f"You may not delete or deselect {instance} as canonical until you "
                            f"mark another {instance._meta.model_name} for <a href={link}>{parent._meta.model_name} "
                            f"{parent}</a> as canonical."
                        )
                    }
                )


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    profile, created = Profile.objects.get_or_create(user=instance)
    profile.save()


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "observations.Profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
    )
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "observations.Profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
    )

    class Meta:
        abstract = True


class CanonicalModel(BaseModel):
    canonical = models.BooleanField(default=False)

    @property
    def parent(self):
        raise NotImplementedError(
            "subclasses of CanonicalModel must provide a parent attribute"
        )

    def get_family(self):
        parent = getattr(self, self.parent._meta.model_name)
        kwargs = {f"{parent._meta.model_name}__exact": parent.pk}
        model = type(self)
        siblings = model.objects.filter(**kwargs).exclude(pk=self.pk)
        return parent, siblings

    def save(self, *args, **kwargs):
        parent, siblings = self.get_family()
        ensure_canonical(self, parent, siblings)
        super().save(*args, **kwargs)

    def save_simple(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        parent, siblings = self.get_family()
        ensure_canonical(self, parent, siblings, "delete")
        super().delete(*args, **kwargs)
        if siblings.count() == 0:
            parent.delete()

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

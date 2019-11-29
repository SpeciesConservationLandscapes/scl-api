from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django_countries.fields import CountryField
# countries: 'USDOS/LSIB/2013' https://developers.google.com/earth-engine/datasets/catalog/USDOS_LSIB_2013


class Profile(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('self', on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='%(class)s_updated_by')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    countries = CountryField(multiple=True)

    class Meta:
        ordering = ('last_name', 'first_name',)

    def __str__(self):
        return '{} [{}]'.format(self.full_name, self.pk)

    @property
    def full_name(self):
        name = []
        if self.first_name:
            name.append(self.first_name)

        if self.last_name:
            name.append(self.last_name)

        if len(name) > 0:
            return ' '.join(name)
        else:
            try:
                email_name = self.email.split('@')[0]
                return email_name
            except IndexError:
                return ''


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('Profile', on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='%(class)s_created_by')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('Profile', on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='%(class)s_updated_by')

    class Meta:
        abstract = True


class Genus(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = _('genera')

    def __str__(self):
        return _('%s') % self.name


class Species(BaseModel):
    name = models.CharField(max_length=100)
    genus = models.ForeignKey(Genus, on_delete=models.CASCADE)
    name_common = models.CharField(max_length=255, blank=True, verbose_name=_('common name (English)'))
    colid = models.CharField(max_length=32, verbose_name=_('Catalog of Life ID'), unique=True)
    # http://apiv3.iucnredlist.org/api/v3/species/id/15955?token=9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee
    iucnid = models.PositiveIntegerField(verbose_name=_('IUCN ID'), unique=True)

    @property
    def ee_path(self):
        if settings.EE_SCL_ROOTDIR is None:
            return None
        return '{}/{}_{}/aoi'.format(settings.EE_SCL_ROOTDIR, self.genus.name.capitalize(), self.name)

    class Meta:
        ordering = ('genus', 'name',)
        verbose_name_plural = _('species')

    def __str__(self):
        return _('%s %s') % (self.genus.name, self.name)


class Biome(BaseModel):
    ee_path = 'RESOLVE/ECOREGIONS/2017'
    name = models.CharField(max_length=100)
    biomeid = models.PositiveIntegerField(verbose_name=_('RESOLVE ecoregion biome number'), unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return _(u'%s') % self.name


class ProtectedArea(BaseModel):
    ee_path = 'WCMC/WDPA/current/polygons'
    name = models.CharField(max_length=255)
    wdpaid = models.PositiveIntegerField(verbose_name=_('WDPA ID'), unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('protected area')
        verbose_name_plural = _('protected areas')

    def __str__(self):
        return _('%s') % self.name


class SCL(BaseModel):
    CLASS_CHOICES = (
        (1, 'I'),
        (2, 'II'),
        (3, 'III'),
        (4, 'IV'),
    )

    name = models.CharField(max_length=255)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    # What is in 2006 tcl data -- but probably restoration, survey, and fragment are different "types"
    sclclass = models.PositiveSmallIntegerField(
        choices=CLASS_CHOICES,
        null=True, blank=True,
        verbose_name=_('SCL class')
    )

    @property
    def ee_path(self):
        if settings.EE_SCL_ROOTDIR is None:
            return None
        return '{}/{}_{}/scl'.format(settings.EE_SCL_ROOTDIR, self.species.genus.name.capitalize(), self.name)

    class Meta:
        ordering = ('name', 'species',)
        verbose_name = _('species conservation landscape')
        verbose_name_plural = _('species conservation landscapes')

    def __str__(self):
        return _('%s [%s]') % (self.name, self.species)


class SCLStats(BaseModel):
    scl = models.ForeignKey(SCL, on_delete=models.CASCADE)
    country = CountryField()
    biome = models.ForeignKey(Biome, on_delete=models.CASCADE)
    pa = models.ForeignKey(ProtectedArea, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    area = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal('0.00'))

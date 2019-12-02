from django.db import models
from django.utils.translation import ugettext_lazy as _
# countries: 'USDOS/LSIB/2013' https://developers.google.com/earth-engine/datasets/catalog/USDOS_LSIB_2013
from django_countries.fields import CountryField


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


class Profile(BaseModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    countries = CountryField(multiple=True, blank=True)

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


class AuthUser(BaseModel):
    profile = models.ForeignKey(Profile, related_name='authusers', on_delete=models.CASCADE)
    user_id = models.CharField(unique=True, max_length=255)

    class Meta:
        unique_together = ('profile', 'user_id',)

    def __str__(self):
        return _(u'%s') % self.profile.full_name

# Generated by Django 2.2.12 on 2021-04-21 20:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('observations', '0003_auto_20210330_2223'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Profile',
            new_name='ObsProfile',
        ),
    ]
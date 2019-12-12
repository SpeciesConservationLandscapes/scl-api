# Generated by Django 2.2.6 on 2019-12-12 03:52

from decimal import Decimal
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("api", "0003_auto_20191209_1954")]

    operations = [
        migrations.RemoveField(model_name="fragmentlandscape", name="areas"),
        migrations.RemoveField(model_name="restorationlandscape", name="areas"),
        migrations.RemoveField(model_name="scl", name="areas"),
        migrations.RemoveField(model_name="surveylandscape", name="areas"),
        migrations.AddField(
            model_name="fragmentstats",
            name="area",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=11
            ),
        ),
        migrations.AddField(
            model_name="fragmentstats",
            name="biome_areas",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="restorationstats",
            name="area",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=11
            ),
        ),
        migrations.AddField(
            model_name="restorationstats",
            name="biome_areas",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sclstats",
            name="area",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=11
            ),
        ),
        migrations.AddField(
            model_name="sclstats",
            name="biome_areas",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="surveystats",
            name="area",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=11
            ),
        ),
        migrations.AddField(
            model_name="surveystats",
            name="biome_areas",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]

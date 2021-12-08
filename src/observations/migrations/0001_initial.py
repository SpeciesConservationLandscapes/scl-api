# Generated by Django 2.2.12 on 2021-03-14 20:43

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import observations.models.base


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0007_delete_probabilitycoefficients'),
    ]

    operations = [
        migrations.CreateModel(
            name='DateType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('sequence', models.PositiveSmallIntegerField()),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('examples', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'ordering': ['sequence', 'name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LocalityType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('sequence', models.PositiveSmallIntegerField()),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('examples', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'ordering': ['sequence', 'name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ObservationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('sequence', models.PositiveSmallIntegerField()),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('examples', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'ordering': ['sequence', 'name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='reference')),
                ('name_short', models.CharField(max_length=100, verbose_name='short name')),
                ('year', models.SmallIntegerField(blank=True, null=True)),
                ('zotero', models.CharField(max_length=8, verbose_name='zotero ID')),
                ('description', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reference_created_by', to='observations.Profile')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reference_updated_by', to='observations.Profile')),
            ],
            options={
                'ordering': ['name_short'],
            },
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('canonical', models.BooleanField(default=False)),
                ('page_numbers', models.CharField(blank=True, max_length=50)),
                ('year', models.SmallIntegerField(blank=True, null=True)),
                ('date_text', models.TextField(blank=True)),
                ('sex', models.CharField(choices=[('male', 'male'), ('female', 'female'), ('unknown', 'unknown')], default='unknown', max_length=50)),
                ('age', models.CharField(choices=[('mature', 'mature'), ('immature', 'immature'), ('unknown', 'unknown')], default='unknown', max_length=50)),
                ('observation_text', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('point', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='record_created_by', to='observations.Profile')),
                ('date_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='observations.DateType')),
                ('locality_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='observations.LocalityType')),
                ('observation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='observations.Observation')),
                ('observation_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='observations.ObservationType')),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='observations.Reference')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='record_updated_by', to='observations.Profile')),
            ],
            options={
                'ordering': ['observation_id', '-canonical', 'year', 'reference__name_short'],
            },
        ),
        migrations.CreateModel(
            name='ObservationTypeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observationtypegroup_created_by', to='observations.Profile')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observationtypegroup_updated_by', to='observations.Profile')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='observationtype',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observationtype_created_by', to='observations.Profile'),
        ),
        migrations.AddField(
            model_name='observationtype',
            name='observation_type_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='observations.ObservationTypeGroup'),
        ),
        migrations.AddField(
            model_name='observationtype',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observationtype_updated_by', to='observations.Profile'),
        ),
        migrations.AddField(
            model_name='observation',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observation_created_by', to='observations.Profile'),
        ),
        migrations.AddField(
            model_name='observation',
            name='species',
            field=models.ForeignKey(default=observations.models.base.default_species, on_delete=django.db.models.deletion.PROTECT, to='api.Species'),
        ),
        migrations.AddField(
            model_name='observation',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observation_updated_by', to='observations.Profile'),
        ),
        migrations.AddField(
            model_name='localitytype',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='localitytype_created_by', to='observations.Profile'),
        ),
        migrations.AddField(
            model_name='localitytype',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='localitytype_updated_by', to='observations.Profile'),
        ),
        migrations.AddField(
            model_name='datetype',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='datetype_created_by', to='observations.Profile'),
        ),
        migrations.AddField(
            model_name='datetype',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='datetype_updated_by', to='observations.Profile'),
        ),
    ]
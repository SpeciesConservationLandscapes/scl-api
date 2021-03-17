# Generated by Django 2.2.12 on 2021-03-17 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='locality_text',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='age',
            field=models.CharField(choices=[('adult', 'adult'), ('adult - uncertain', 'adult - uncertain'), ('immature', 'immature'), ('immature - uncertain', 'immature - uncertain'), ('unknown', 'unknown')], default='unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='record',
            name='sex',
            field=models.CharField(choices=[('male', 'male'), ('male - uncertain', 'male - uncertain'), ('female', 'female'), ('female - uncertain', 'female - uncertain'), ('unknown', 'unknown')], default='unknown', max_length=50),
        ),
    ]

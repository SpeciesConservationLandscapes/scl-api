import argparse
import csv
import sys
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from api.models import Species
from observations.models import (
    Observation,
    Profile,
    Reference,
    Record,
    DateType,
    LocalityType,
    ObservationType,
)

# from osgeo import ogr


class Command(BaseCommand):
    help = "Ingest historical species observations from a shapefile."
    species_choices = [s.full_name for s in Species.objects.all()]
    default_species = "Panthera tigris"
    format_choices = ("csv", "shp")
    sex_choices = {
        "f": "female",
        "f?": "female - uncertain",
        "m": "male",
        "m?": "male - uncertain",
    }
    age_choices = {
        "a": "adult",
        "a?": "adult - uncertain",
        "sa": "immature",
        "sa?": "immature - uncertain",
        "j": "immature",
    }
    default_profile_pk = 1

    def add_arguments(self, parser):
        parser.add_argument("datafile", nargs=1, type=argparse.FileType("r"))
        parser.add_argument(
            "--species",
            nargs="?",
            choices=self.species_choices,
            default=self.default_species,
            help="Scientific name of species; defaults to 'Panthera tigris'.",
        )
        parser.add_argument(
            "--profile",
            nargs="?",
            default=self.default_profile_pk,
            help="PK of user profile.",
        )
        parser.add_argument(
            "-f",
            "--format",
            nargs="?",
            choices=self.format_choices,
            default="csv",
            help="Ingestion source file format: shapefile ('shp') or 'csv'; defaults to 'csv'.",
        )
        parser.add_argument(
            "--dryrun",
            action="store_true",
            help="Runs ingest in a database transaction, then does a rollback.",
        )

    def _get_lookup(self, model, field, value):
        try:
            obj = model.objects.get(**{field: value})
            return obj
        except model.DoesNotExist as err:
            self.stderr.write(f"No {model._meta.model_name} with {field} = {value}")
            raise err

    def handle(self, *args, **options):
        datafile = options["datafile"][0]
        # TODO: once this is working, abstract it out into a function somewhere else general?
        if options["format"] != "csv":
            raise NotImplementedError(
                f"Ingestion of {options['format']} files not yet implemented."
            )
        genus, name = options["species"].split(" ")
        species = Species.objects.get(genus__name=genus, name=name)
        profile = Profile.objects.get(pk=options["profile"])
        reader = csv.DictReader(datafile)

        try:
            with transaction.atomic():
                sid = transaction.savepoint()

                try:
                    recordcount = 0
                    observations = {}
                    for row in reader:
                        observation = observations.setdefault(
                            row["Observation Id"],
                            Observation.objects.create(
                                species=species, created_by=profile, updated_by=profile
                            ),
                        )
                        created_by = profile
                        updated_by = profile
                        canonical = bool(row["Canonical"])
                        year = None
                        if int(row["Year"]) > 0:
                            year = int(row["Year"])
                        reference = self._get_lookup(
                            Reference, "name_short", row["Reference"]
                        )
                        date_type = self._get_lookup(DateType, "name", row["Date type"])
                        locality_type = self._get_lookup(
                            LocalityType, "name", row["Locality type"]
                        )
                        observation_type = self._get_lookup(
                            ObservationType, "name", row["Observation type"]
                        )
                        date_text = row["Date text"]
                        locality_text = row["Locality text"]
                        observation_text = row["Observation text"]
                        sex = Record.UNKNOWN
                        if row["Sex"] in self.sex_choices.keys():
                            sex = self.sex_choices[row["Sex"]]
                        age = Record.UNKNOWN
                        if row["Age"] in self.age_choices.keys():
                            age = self.age_choices[row["Age"]]
                        notes = row["Notes"]
                        lat = float(row["Latitude"])
                        lon = float(row["Longitude"])
                        point = Point(x=lon, y=lat, srid=4326)

                        try:
                            # https://code.djangoproject.com/ticket/27314
                            Record.objects.create(
                                observation=observation,
                                created_by=created_by,
                                updated_by=updated_by,
                                canonical=canonical,
                                year=year,
                                reference=reference,
                                date_type=date_type,
                                locality_type=locality_type,
                                observation_type=observation_type,
                                date_text=date_text,
                                locality_text=locality_text,
                                observation_text=observation_text,
                                sex=sex,
                                age=age,
                                notes=notes,
                                point=point,
                            )
                            recordcount += 1
                        except IntegrityError as e:
                            pass

                finally:
                    if options["dryrun"] is True:
                        self.stdout.write(
                            f"dryrun: {recordcount} records would have been written."
                        )
                        transaction.savepoint_rollback(sid)
                    else:
                        self.stdout.write(f"{recordcount} records written.")
                        transaction.savepoint_commit(sid)

        except Exception as err:
            transaction.savepoint_rollback(sid)
            self.stderr.write(str(err))
            sys.exit(1)

        # driver = ogr.GetDriverByName('ESRI Shapefile')
        # ds = driver.Open(datafile, 0)
        # if ds is None:
        #     self.stderr.write(f"Could not open {datafile} as a shapefile")
        #     sys.exit(1)
        # layer = ds.GetLayer()
        # feature_count = layer.GetFeatureCount()
        # if feature_count < 1:
        #     self.stderr.write("No features in shapefile to ingest")
        #     sys.exit(0)
        # validate crs, geometry type, and # of features

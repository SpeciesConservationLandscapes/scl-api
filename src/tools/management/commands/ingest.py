import os
import json
import sys
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.apps import apps
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.conf import settings
from google.cloud import storage
from google.oauth2 import service_account
from ....api.models import *


def _get_landscape_vars(landscape_key):
    landscape_model = None
    stats_model = None
    landscape_property = ""
    if landscape_key == "scl_species":
        landscape_model = apps.get_model(app_label="api", model_name="SCL")
        stats_model = apps.get_model(app_label="api", model_name="SCLStats")
        landscape_property = "scl"
    elif landscape_key == "scl_restoration":
        landscape_model = apps.get_model(
            app_label="api", model_name="RestorationLandscape"
        )
        stats_model = apps.get_model(app_label="api", model_name="RestorationStats")
        landscape_property = "restoration_landscape"
    elif landscape_key == "scl_survey":
        landscape_model = apps.get_model(app_label="api", model_name="SurveyLandscape")
        stats_model = apps.get_model(app_label="api", model_name="SurveyStats")
        landscape_property = "survey_landscape"
    elif landscape_key == "scl_fragment":
        landscape_model = apps.get_model(
            app_label="api", model_name="FragmentLandscape"
        )
        stats_model = apps.get_model(app_label="api", model_name="FragmentStats")
        landscape_property = "fragment"

    return landscape_model, stats_model, landscape_property


def ingest_landscapes(landscape_key, species, scldate, countries_biomes_pas):
    landscape_model, stats_model, landscape_property = _get_landscape_vars(
        landscape_key
    )

    count = 0
    for countries_biomes_pa in countries_biomes_pas["features"]:
        props = countries_biomes_pa["properties"]

        # TODO: add eeid for landscape when we have it
        attribs = {"species": species, "date": scldate}
        if landscape_key == "scl_species":
            attribs["name"] = props.get("lsname", "")
            attribs["sclclass"] = props.get("lsclass", "")
        landscape, _ = landscape_model.objects.get_or_create(**attribs)

        geom = GEOSGeometry(json.dumps(countries_biomes_pa["geometry"]))
        if geom.geom_type == "Polygon":
            geom = MultiPolygon([geom])

        stats_attribs = {
            landscape_property: landscape,
            "country": props["lscountry"],
            "area": props["lscountry_area"],
            "biome_areas": props["areas"],
        }
        s, _ = stats_model.objects.get_or_create(**stats_attribs)
        if _:  # Can't include geom in get_or_create with geography=True
            s.geom = geom
            s.save()
            count += 1

    return count


class Command(BaseCommand):
    help = "Update SCL statistics from geojson files produced by SCL pipeline."

    def __init__(self):
        super(Command, self).__init__()
        self.local_restore_dir = os.path.join(os.path.sep, "tmp", "scl")
        try:
            os.mkdir(self.local_restore_dir)
        except OSError:
            pass  # Means it already exists.
        key = json.loads(settings.GCP_SERVICE_ACCOUNT_KEY)
        credentials = service_account.Credentials.from_service_account_info(key)
        self.client = storage.Client(
            project=settings.GCP_PROJECT_ID, credentials=credentials
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Runs ingest in a database transaction, then does a rollback.",
        )

    def handle(self, dry_run, *args, **options):
        try:
            with transaction.atomic():
                speciess = Species.objects.all()
                for species in speciess:
                    species_slug = species.full_name.replace(" ", "_")
                    bucket_file_list = self.client.list_blobs(
                        settings.GCP_BUCKET_SCLS,
                        prefix="ls_stats/{}".format(species_slug),
                    )
                    blobs = []
                    datafiles = []
                    for obj in bucket_file_list:
                        filename = os.path.join(
                            self.local_restore_dir, obj.name.replace("/", "_")
                        )
                        # scl-pipeline/ls_stats/Panthera_tigris/2006-01-01
                        if not os.path.isfile(filename):
                            print("Downloading {} to {} ".format(obj.name, filename))
                            obj.download_to_filename(filename)
                            if not os.path.isfile(filename):
                                raise ValueError("File did not download")
                        filedate = obj.name.split("/")[-2]
                        landscape_key = obj.name.split("/")[-1].split(".")[0]
                        datafiles.append((filename, filedate, landscape_key))
                        blobs.append(obj)

                    if len(datafiles) < 1:
                        continue

                    successes = []
                    for (datafile, scldate, landscape_key) in datafiles:
                        sid = transaction.savepoint()
                        success = False
                        count = 0
                        try:
                            with open(datafile) as f:
                                countries_biomes_pas = json.load(f)
                                count = ingest_landscapes(
                                    landscape_key,
                                    species,
                                    scldate,
                                    countries_biomes_pas,
                                )
                                success = True
                                successes.append(datafile)

                        finally:
                            if dry_run is True or success is False:
                                transaction.savepoint_rollback(sid)
                                msg = "{} features would have been ingested from {}"
                            else:
                                transaction.savepoint_commit(sid)
                                msg = "{} features were ingested from {}"
                            print(msg.format(count, datafile))
                            os.remove(datafile)

                    if (
                        len(successes) == len(datafiles)
                        and settings.ENVIRONMENT == "prod"
                    ):
                        for obj in blobs:
                            obj.delete()

        except Exception as err:
            transaction.savepoint_rollback(sid)
            self.stderr.write(str(err))
            sys.exit(1)

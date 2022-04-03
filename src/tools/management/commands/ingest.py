import os
import json
import sys
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.apps import apps
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from google.cloud import storage
from google.oauth2 import service_account
from api.models import *
from api.utils import round_recursive


INDIGENOUS_RANGE_FILE = "country_historical_range.geojson"


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
    elif landscape_key == "scl_species_fragment":
        landscape_model = apps.get_model(
            app_label="api", model_name="SpeciesFragmentLandscape"
        )
        stats_model = apps.get_model(app_label="api", model_name="SpeciesFragmentStats")
        landscape_property = "species_fragment"
    elif landscape_key == "scl_restoration_fragment":
        landscape_model = apps.get_model(
            app_label="api", model_name="RestorationFragmentLandscape"
        )
        stats_model = apps.get_model(
            app_label="api", model_name="RestorationFragmentStats"
        )
        landscape_property = "restoration_fragment"
    elif landscape_key == "scl_survey_fragment":
        landscape_model = apps.get_model(
            app_label="api", model_name="SurveyFragmentLandscape"
        )
        stats_model = apps.get_model(app_label="api", model_name="SurveyFragmentStats")
        landscape_property = "survey_fragment"

    return landscape_model, stats_model, landscape_property


def get_multipolygon(geojson_geom):
    geom = GEOSGeometry(json.dumps(geojson_geom))
    if geom.geom_type == "Polygon":
        geom = MultiPolygon([geom])
    return geom


def ingest_landscapes(landscape_key, species, scldate, countries_biomes_pas):
    landscape_model, stats_model, landscape_property = _get_landscape_vars(
        landscape_key
    )

    count = 0
    for countries_biomes_pa in countries_biomes_pas["features"]:
        props = countries_biomes_pa["properties"]

        attribs = {"lsid": props.get("lsid"), "species": species, "date": scldate}
        if landscape_key == "scl_species":
            attribs["name"] = props.get("lsname", "")
        landscape, _ = landscape_model.objects.get_or_create(**attribs)

        stats_attribs = round_recursive(
            {
                landscape_property: landscape,
                "country": props["lscountry"],
                "area": props["lscountry_area"],
                "biome_areas": props["areas"],
            },
            4,
        )
        s, created = stats_model.objects.get_or_create(**stats_attribs)
        if created:  # Can't include geom in get_or_create with geography=True
            s.geom = get_multipolygon(countries_biomes_pa["geometry"])
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
        self.dry_run = False
        self.indigenous = False
        self.files = {}

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Runs ingest in a database transaction, then does a rollback.",
        )
        parser.add_argument(
            "--indigenous",
            action="store_true",
            help="Ingest (overwrite) species indigenous range stats.",
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.indigenous = options["indigenous"]
        try:
            with transaction.atomic():
                speciess = Species.objects.all()
                for species in speciess:
                    self.get_files(species)
                    if len(self.files[species]["ls_datafiles"]) < 1:
                        continue

                    sid = transaction.savepoint()
                    ls_successes = self.process_ls_files(species)
                    indigenous_success = self.ingest_indigenous_range(
                        species, self.files[species]["indigenous"]
                    )

                    if (
                        len(ls_successes) == len(self.files[species]["ls_datafiles"])
                        and indigenous_success
                        and not self.dry_run
                    ):
                        transaction.savepoint_commit(sid)
                        if settings.ENVIRONMENT == "prod":
                            for obj in self.files[species]["blobs"]:
                                obj.delete()
                    else:
                        transaction.savepoint_rollback(sid)

        except Exception as err:
            transaction.savepoint_rollback(sid)
            self.stderr.write(str(err))
            sys.exit(1)

    def get_files(self, species):
        species_slug = species.full_name.replace(" ", "_")
        bucket_file_list = self.client.list_blobs(
            settings.GCP_BUCKET_SCLS,
            prefix="ls_stats/{}".format(species_slug),
        )
        blobs = []
        ls_datafiles = []
        indigenous_file = None
        for obj in bucket_file_list:
            filename = os.path.join(self.local_restore_dir, obj.name.replace("/", "_"))
            # scl-pipeline/ls_stats/Panthera_tigris/2006-01-01
            if not os.path.isfile(filename):
                self.stdout.write("Downloading {} to {} ".format(obj.name, filename))
                obj.download_to_filename(filename)
                if not os.path.isfile(filename):
                    raise ValueError("File did not download")
            blobs.append(obj)
            if INDIGENOUS_RANGE_FILE in obj.name:
                indigenous_file = filename
            else:
                filedate = obj.name.split("/")[-2]
                landscape_key = obj.name.split("/")[-1].split(".")[0]
                ls_datafiles.append((filename, filedate, landscape_key))

        self.files[species] = {
            "blobs": blobs,
            "ls_datafiles": ls_datafiles,
            "indigenous": indigenous_file,
        }

    def process_ls_files(self, species):
        ls_successes = []
        for (datafile, scldate, landscape_key) in self.files[species]["ls_datafiles"]:
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
                    ls_successes.append(datafile)

            finally:
                msg = "{} features were ingested from {}"
                if self.dry_run or not success:
                    msg = "{} features would have been ingested from {}"
                self.stdout.write(msg.format(count, datafile))
                os.remove(datafile)

        return ls_successes

    def ingest_indigenous_range(self, species, filename):
        if not self.indigenous:
            return True
        if not os.path.isfile(filename):
            self.stderr.write(
                f"Indigenous range file for {species} does not exist; skipping"
            )
            return False

        success = False
        count = 0
        try:
            with open(filename) as f:
                country_irs = json.load(f)
                for country_ir in country_irs["features"]:
                    props = country_ir["properties"]
                    attribs = round_recursive(
                        {
                            "species": species,
                            "country": props["country"],
                            "area": props["area"],
                        },
                        4,
                    )
                    c, created = IndigenousRangeCountryStats.objects.get_or_create(
                        **attribs
                    )
                    if created:
                        c.geom = get_multipolygon(country_ir["geometry"])
                        c.save()
                        count += 1

                success = True

        finally:
            msg = "{} features were ingested from {}"
            if self.dry_run or not success:
                msg = "{} features would have been ingested from {}"
            self.stdout.write(msg.format(count, filename))
            os.remove(filename)

        return success

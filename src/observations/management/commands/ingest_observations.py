import argparse
import sys
from django.core.management.base import BaseCommand, CommandError
from api.models import Species
from osgeo import ogr


class Command(BaseCommand):
    help = "Ingest historical species observations from a shapefile."
    species_choices = [s.full_name for s in Species.objects.all()]
    default_species = "Panthera tigris"

    def add_arguments(self, parser):
        parser.add_argument("datafile", nargs=1, type=argparse.FileType("r"))
        parser.add_argument("--species", nargs="?", choices=self.species_choices, default=self.default_species)
        parser.add_argument(
            "--dryrun",
            action="store_true",
            help="Runs ingest in a database transaction, then does a rollback.",
        )

    def handle(self, datafile, species, dryrun, *args, **options):
        datafile = datafile[0]
        # TODO: once this is working, abstract it out into a function somewhere else general?
        driver = ogr.GetDriverByName('ESRI Shapefile')
        ds = driver.Open(datafile, 0)
        if ds is None:
            self.stderr.write(f"Could not open {datafile} as a shapefile")
            sys.exit(1)
        layer = ds.GetLayer()
        feature_count = layer.GetFeatureCount()
        if feature_count < 1:
            self.stderr.write("No features in shapefile to ingest")
            sys.exit(0)
        # validate crs, geometry type, and # of features

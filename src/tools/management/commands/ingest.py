import argparse
import json
import sys
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon

from api.models import *


class Command(BaseCommand):
    help = "Update SCL statistics from a geojson file produced by SCL pipeline."

    def add_arguments(self, parser):
        # TODO: check bucket for updated results; only run if country/date in geojson filename aren't in db. If not,
        #  download that file and process, instead of just operating on a single file (remove this arg).
        #  filename should be: <species>-<scltype>-<date>.json
        parser.add_argument("datafile", nargs=1, type=argparse.FileType("r"))
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Runs ingest in a database transaction, then does a rollback.",
        )

    def handle(self, datafile, dry_run, *args, **options):
        datafile = datafile[0]

        try:
            with transaction.atomic():
                speciess = Species.objects.all()
                for species in speciess:
                    sid = transaction.savepoint()
                    success = False
                    try:
                        scldate = date(2006, 1, 1)
                        countries_biomes_pas = json.load(datafile)
                        for countries_biomes_pa in countries_biomes_pas["features"]:
                            props = countries_biomes_pa["properties"]

                            scl_attribs = {
                                "species": species,
                                "name": props["scl_name"],
                                "sclclass": props["scl_class"],
                            }
                            scl, _ = SCL.objects.get_or_create(**scl_attribs)

                            geom = GEOSGeometry(
                                json.dumps(countries_biomes_pa["geometry"])
                            )
                            if geom.geom_type == "Polygon":
                                geom = MultiPolygon([geom])

                            stats_attribs = {
                                "scl": scl,
                                "country": props["scl_country"],
                                "date": scldate,
                                "area": props["scl_country_area"],
                                "biome_areas": props["areas"],
                            }
                            s, _ = SCLStats.objects.get_or_create(**stats_attribs)
                            # Can't include geom in get_or_create with geography=True
                            s.geom = geom
                            s.save()
                        success = True

                    finally:
                        if dry_run is True or success is False:
                            transaction.savepoint_rollback(sid)
                        else:
                            transaction.savepoint_commit(sid)

        except Exception as err:
            transaction.savepoint_rollback(sid)
            self.stderr.write(str(err))
            sys.exit(1)

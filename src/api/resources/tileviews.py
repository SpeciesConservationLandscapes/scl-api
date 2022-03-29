import ee
import json
from django.conf import settings
from threading import Timer
from typing import Dict
from .tiles import DatedAssets, DatedTileCollection

use_ee = settings.TILE_SOURCE == "EE"

tilecollections: Dict[str, DatedTileCollection] = {}


def init_ee_creds(refresh: bool = True):

    service_account_name = json.loads(settings.GCP_SERVICE_ACCOUNT_KEY)["client_email"]
    credentials = ee.ServiceAccountCredentials(
        service_account_name, key_data=settings.GCP_SERVICE_ACCOUNT_KEY
    )
    ee.Reset()
    ee.Initialize(credentials)

    for key in tilecollections:
        tilecollections[key].refresh_mapids()

    if refresh is True:
        refresh_time = 72000.0  # 20hrs
        t = Timer(refresh_time, init_ee_creds)
        t.start()


if use_ee:
    if settings.ENVIRONMENT == "prod":
        init_ee_creds()
    else:
        init_ee_creds(refresh=False)

    hii_assets = DatedAssets.fetch_assets(
        asset_directory="projects/earthengine-legacy/assets",
        ee_directory="projects/HII/v1/hii",
        adjust_date=True,
    )
else:
    hii_assets = DatedAssets.empty()
    print("not using ee")

hii_tiles_rainbow = DatedTileCollection(
    name="legacy",
    dated_assets=hii_assets,
    viz_params={
        "min": 0,
        "max": 6200,
        "palette": [
            "00734c",
            "38a800",
            "ffff00",
            "ff0000",
            "4c0073",
            "000000",
        ],
    },
)
tilecollections[hii_tiles_rainbow.name] = hii_tiles_rainbow

hii_tiles_purple = DatedTileCollection(
    name="purple",
    dated_assets=hii_assets,
    viz_params={
        "min": 0,
        "max": 6200,
        "palette": [
            "ffffff",
            "8400a8",
            "4c0073",
            "000000",
        ],
    },
)
tilecollections[hii_tiles_purple.name] = hii_tiles_purple

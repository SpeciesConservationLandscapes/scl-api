import ee
import json
from django.conf import settings
from threading import Timer
from typing import Dict
from .tiles import DatedImageAssets, DatedTileCollection, FCTileAssets, FCTileCollection, TileCollection

use_ee = settings.TILE_SOURCE == "EE"

tilecollections: Dict[str, TileCollection] = {}
hii_assets = DatedImageAssets.empty()
biome_assets = FCTileAssets.empty()
pa_assets = FCTileAssets.empty()
pa_filters = []
kba_assets = FCTileAssets.empty()
structuralhabitat_assets = DatedImageAssets.empty()


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

    hii_assets = DatedImageAssets.fetch_assets(
        asset_directory="projects/earthengine-legacy/assets/projects/HII/v1/hii",
        adjust_date=True
    )
    biome_assets = FCTileAssets.fetch_assets(
        asset_id="RESOLVE/ECOREGIONS/2017"
    )
    pa_assets = FCTileAssets.fetch_assets(asset_id="WCMC/WDPA/current/polygons")
    # TODO: make pas date-aware by filtering on lte(STATUS_YR)
    pa_filters = [ee.Filter.neq("STATUS", "Proposed")]
    kba_assets = FCTileAssets.fetch_assets(asset_id="projects/SCL/v1/source/KBAsGlobal_20200301")
    structuralhabitat_assets = DatedImageAssets.fetch_assets(
        asset_directory="projects/earthengine-legacy/assets/projects/SCL/v1/Panthera_tigris/canonical/structural_habitat",
        adjust_date=True
    )

hii_tiles_rainbow = DatedTileCollection(
    name="hii-legacy",
    assets=hii_assets,
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
    name="hii-purple",
    assets=hii_assets,
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

biometiles = FCTileCollection(
    name="biomes",
    assets=biome_assets,
    viz_params={
        "palette": [
            "#38A700",
            "#CCCD65",
            "#88CE66",
            "#00734C",
            "#458970",
            "#7AB6F5",
            "#FEAA01",
            "#FEFF73",
            "#BEE7FF",
            "#D6C39D",
            "#9ED7C2",
            "#FE0000",
            "#CC6767",
            "#FE01C4",
        ],
        "max": 14,
    },
    color="BIOME_NUM"
)
tilecollections[biometiles.name] = biometiles

patiles = FCTileCollection(
    name="pas",
    assets=pa_assets,
    filters=pa_filters,
    viz_params={"palette": "#14A51C"},
    color=1
)
tilecollections[patiles.name] = patiles

kbatiles = FCTileCollection(
    name="kbas",
    assets=kba_assets,
    viz_params={"palette": "#14A51C"},
    color=1
)
tilecollections[kbatiles.name] = kbatiles

structuralhabitattiles = DatedTileCollection(
    name="structural-habitat",
    assets=structuralhabitat_assets,
    viz_params={"min": 3, "max": 30, "palette": ["white", "009900"]}
)
tilecollections[structuralhabitattiles.name] = structuralhabitattiles

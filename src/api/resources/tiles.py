import json
from threading import Timer

import requests
import ee
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, APIException
from .base import UserAtLeastOneCountryPermission


def init_ee_creds():
    refresh_time = 72000.0  # 20hrs
    service_account_name = json.loads(settings.GCP_SERVICE_ACCOUNT_KEY)["client_email"]
    credentials = ee.ServiceAccountCredentials(
        service_account_name, key_data=settings.GCP_SERVICE_ACCOUNT_KEY
    )
    ee.Initialize(credentials)
    t = Timer(refresh_time, init_ee_creds)
    t.start()


init_ee_creds()

# https://developers.google.com/earth-engine/feature_collections_visualizing?hl=en
empty = ee.Image().byte()

mapids = {
    "biomes": empty.paint(
        featureCollection=ee.FeatureCollection("RESOLVE/ECOREGIONS/2017"),
        color="BIOME_NUM",
    ).getMapId(
        {
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
        }
    ),
    "pas": empty.paint(
        featureCollection=ee.FeatureCollection("WCMC/WDPA/current/polygons"),
        color=1,
        # width=1,
    ).getMapId({"palette": "#14A51C"}),
    "hii": ee.ImageCollection("projects/HII/v1/hii")
    .sort("system:index", False)
    .first()
    .getMapId(
        {
            "min": 1,
            "max": 50,
            "palette": [
                "224f1a",
                "a3ff76",
                "feff6f",
                "a09568",
                "ffa802",
                "f7797c",
                "fb0102",
                "d87136",
                "a90086",
                "7a1ca5",
                "421137",
                "000000",
            ],
        }
    ),
    "species": {
        "Panthera_tigris": empty.paint(
            featureCollection=ee.FeatureCollection(
                "projects/SCL/v1/Panthera_tigris/aoi"
            ),
            color="000000",
            width=3,
        ).getMapId()
    },
}


class PngRenderer(BaseRenderer):
    media_type = "image/png"
    format = "png"
    charset = None
    render_style = "binary"

    def render(self, data, media_type=None, renderer_context=None):
        return data


class TileView(APIView):
    renderer_classes = (PngRenderer,)
    permission_classes = [UserAtLeastOneCountryPermission]
    layer = None

    def __init__(self, layer=None):
        if not layer or layer not in mapids:
            raise APIException("Missing or incorrect tile layer")
        self.layer = mapids[layer]
        super().__init__()

    def get(self, request, z, x, y, species=None):
        x = int(x)
        y = int(y)
        z = int(z)
        if species and species in mapids["species"]:
            self.layer = mapids["species"][species]

        tile_url = ee.data.getTileUrl(self.layer, x, y, z)
        resp = requests.get(tile_url)
        status_code = resp.status_code
        if status_code == 404:
            raise NotFound()
        if status_code >= 500:
            raise APIException()
        return Response(data=resp.content, content_type="image/png")

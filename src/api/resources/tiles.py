import json
import requests
import ee
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound, APIException


service_account_name = json.loads(settings.EE_SERVICE_ACCOUNT_KEY)["client_email"]
credentials = ee.ServiceAccountCredentials(
    service_account_name, key_data=settings.EE_SERVICE_ACCOUNT_KEY
)
ee.Initialize(credentials)

# https://developers.google.com/earth-engine/feature_collections_visualizing?hl=en
empty = ee.Image().byte()

mapids = {
    "biomes": empty.paint(
        featureCollection=ee.FeatureCollection("RESOLVE/ECOREGIONS/2017"),
        color="BIOME_NUM",
    ).getMapId(
        {
            "palette": [
                "a6cee3",
                "1f78b4",
                "b2df8a",
                "33a02c",
                "fb9a99",
                "e31a1c",
                "fdbf6f",
                "ff7f00",
                "cab2d6",
                "6a3d9a",
                "ffff99",
                "b15928",
                "8dd3c7",
                "b3de69",
            ],
            "max": 14,
        }
    ),
    "pas": empty.paint(
        featureCollection=ee.FeatureCollection("WCMC/WDPA/current/polygons"),
        color="2ca25f",
        width=3,
    ).getMapId(),
    "hii": ee.ImageCollection("projects/HII/v1/hii")
    .sort("system:index", False)
    .first()
    .getMapId(
        {
            "min": 0,
            "max": 100,
            "palette": ["4df309", "fbff0f", "ffab11", "ed1043", "8e13ff", "000000"],
        }
    ),
    "species": {
        "Panthera_tigris": empty.paint(
            featureCollection=ee.FeatureCollection(
                "projects/SCL/v1/Panthera_tigris/scl_poly/2006-01-01/scl-species"
            ),
            color="000000",
            width=4,
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

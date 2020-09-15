import ee
import json
import requests
from datetime import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, APIException
from threading import Timer
from .base import UserAtLeastOneCountryPermission

ROOTDIR = "projects/SCL/v1"
DATE_FORMAT = "%Y-%m-%d"
DATE_FORMAT_EE = "yyyy-MM-dd"
ASSET_TIMESTAMP_PROPERTY = "startTime"

service_account_name = json.loads(settings.GCP_SERVICE_ACCOUNT_KEY)["client_email"]
credentials = ee.ServiceAccountCredentials(
    service_account_name, key_data=settings.GCP_SERVICE_ACCOUNT_KEY
)
ee.Initialize(credentials)
# def init_ee_creds():
#     refresh_time = 72000.0  # 20hrs
#     service_account_name = json.loads(settings.GCP_SERVICE_ACCOUNT_KEY)["client_email"]
#     credentials = ee.ServiceAccountCredentials(
#         service_account_name, key_data=settings.GCP_SERVICE_ACCOUNT_KEY
#     )
#     ee.Initialize(credentials)
#     t = Timer(refresh_time, init_ee_creds)
#     t.start()
#
#
# init_ee_creds()

# https://developers.google.com/earth-engine/feature_collections_visualizing?hl=en
empty = ee.Image().byte()

mapids = {
    "hii": {},
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
    "aoi": {
        "Panthera_tigris": empty.paint(
            featureCollection=ee.FeatureCollection(f"{ROOTDIR}/Panthera_tigris/historical_range_200914"),
            color="000000",
            width=3,
        ).getMapId()
    },
    "structural_habitat": {"Panthera_tigris": {}},
}


def get_assets(eedir):
    assets = []
    # possible ee api bug requires prepending
    assetdir = f"projects/earthengine-legacy/assets/{eedir}"
    try:
        assets = ee.data.listAssets({"parent": assetdir})["assets"]
    except ee.ee_exception.EEException:
        print(f"Folder {eedir} does not exist or is not a folder/image collection.")
    return assets


hii_images = get_assets("projects/HII/v1/sumatra_poc/hii")
for hii in hii_images:
    try:
        date = ee.Date(hii[ASSET_TIMESTAMP_PROPERTY])
    except ee.ee_exception.EEException:
        continue

    date = date.format(DATE_FORMAT_EE).getInfo()
    mapids["hii"][date] = ee.Image(hii["id"]).getMapId(
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
    )
mapids["hii"] = dict(sorted(mapids["hii"].items(), reverse=True))

hab_tiger = get_assets(f"{ROOTDIR}/Panthera_tigris/structural_habitat")
for hab in hab_tiger:
    try:
        date = ee.Date(hab[ASSET_TIMESTAMP_PROPERTY])
    except ee.ee_exception.EEException:
        continue

    date = date.format(DATE_FORMAT_EE).getInfo()
    sh = ee.Image(hab["id"])
    mapids["structural_habitat"]["Panthera_tigris"][date] = sh.updateMask(
        sh.gte(3)
    ).getMapId({"min": 3, "max": 30, "palette": ["white", "009900"]})
mapids["structural_habitat"]["Panthera_tigris"] = dict(
    sorted(mapids["structural_habitat"]["Panthera_tigris"].items(), reverse=True)
)


class PngRenderer(BaseRenderer):
    media_type = "image/png"
    format = "png"
    charset = None
    render_style = "binary"

    def render(self, data, media_type=None, renderer_context=None):
        return data


class TileView(APIView):
    permission_classes = [UserAtLeastOneCountryPermission]
    layer = None

    def _get_mapid(self, species=None, date=None):
        dated_mapid = None
        mapid_date = None
        mapid = mapids[self.layer]
        if species and species in mapids[self.layer]:
            mapid = mapids[self.layer][species]

        for image_date, image in mapid.items():
            try:
                datetime.strptime(image_date, DATE_FORMAT)
                dated_mapid = mapid[image_date]
                mapid_date = image_date
                if image_date <= date:
                    break
            except ValueError:
                pass  # not broken down by date

        if dated_mapid:
            mapid = dated_mapid
        return mapid, mapid_date

    def __init__(self, layer=None):
        if not layer or layer not in mapids:
            raise APIException("Missing or incorrect tile layer")
        self.layer = layer
        super().__init__()

    def get(self, request, z, x, y, species=None):
        x = int(x)
        y = int(y)
        z = int(z)
        date = request.query_params.get("date", datetime.utcnow().strftime(DATE_FORMAT))
        mapid, mapid_date = self._get_mapid(species, date)

        if "get_date" in request.query_params:
            request.accepted_renderer = JSONRenderer()
            return Response(mapid_date)
        else:
            request.accepted_renderer = PngRenderer()
            tile_url = ee.data.getTileUrl(mapid, x, y, z)
            resp = requests.get(tile_url)
            status_code = resp.status_code
            if status_code == 404:
                raise NotFound()
            if status_code >= 500:
                raise APIException()
            return Response(data=resp.content, content_type="image/png")

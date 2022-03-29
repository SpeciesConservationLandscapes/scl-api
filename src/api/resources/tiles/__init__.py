import os
import typing

import ee
import requests
from django.urls import path
from rest_framework.exceptions import APIException, NotFound
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

DATE_FORMAT = "%Y-%m-%d"
DATE_FORMAT_EE = "yyyy-MM-dd"
ASSET_TIMESTAMP_PROPERTY = "startTime"


class DatedAssets:
    """
    - List Assets from a particular Earth Engine Directory
    - Filter to those with 'startTime' attribute
    - return dictionary {date:asset id}, and list of dates as string 'yyyy-mm-dd'

    - If adjust_date is True, subtracts one day from date
    - requires that ee.Initialize() has been run
    """

    asset_ids: typing.Dict[str, str] = {}
    dates: typing.List[str] = []

    def __init__(self, asset_ids: typing.Dict[str, str]) -> None:
        self.asset_ids = asset_ids
        self.dates = list(sorted(self.asset_ids.keys()))

    @classmethod
    def empty(cls):
        return cls({})

    @classmethod
    def fetch_assets(
        cls, asset_directory: str, ee_directory: str, adjust_date: bool = False
    ):

        directory = os.path.join(asset_directory, ee_directory)

        assets = cls._list_assets(directory)

        asset_ids = {}
        for asset in assets:
            if ASSET_TIMESTAMP_PROPERTY not in asset:
                continue
            try:
                date = ee.Date(asset[ASSET_TIMESTAMP_PROPERTY])
                if adjust_date is True:
                    date = date.advance(-1, "day")
            except ee.ee_exception.EEException:
                continue

            date = date.format(DATE_FORMAT_EE).getInfo()

            asset_ids[date] = asset["id"]

        return cls(asset_ids)

    @classmethod
    def _list_assets(cls, directory):
        try:
            assets = ee.data.listAssets({"parent": directory})["assets"]
        except ee.ee_exception.EEException:
            raise ValueError(
                f"Folder {directory} does not exist or is not a folder/image collection."
            )
        return assets


class PngRenderer(BaseRenderer):
    media_type = "image/png"
    format = "png"
    charset = None
    render_style = "binary"

    def render(self, data, media_type=None, renderer_context=None):
        return data


class TileView(APIView):
    """
    calls ee.data.getTileUrl() on RawMapId.
    Fetches tile from google using that url, and returns it
    """

    tilecollection = None
    date = None

    def __init__(self, tilecollection, date):
        self.tilecollection = tilecollection
        self.date = date
        super().__init__()

    @property
    def mapid(self):
        return self.tilecollection.mapids[self.date]

    def get(self, request, z, x, y):
        x = int(x)
        y = int(y)
        z = int(z)

        request.accepted_renderer = PngRenderer()
        tile_url = ee.data.getTileUrl(self.mapid, x, y, z)
        resp = requests.get(tile_url)
        status_code = resp.status_code
        if status_code == 404:
            raise NotFound()
        if status_code >= 500:
            raise APIException()
        return Response(data=resp.content, content_type="image/png")


class DatesView(APIView):
    """
    Returns a list of the dates
    """

    dates = None

    def __init__(self, dates=None) -> None:
        self.dates = dates
        super().__init__()

    def get(self, request):
        request.accepted_renderer = JSONRenderer()
        return Response([date for date in self.dates])


class DatedTileCollection:
    """
    - for each asset in dated_assets, get mapids, applying visualization parameters
      (https://developers.google.com/earth-engine/apidocs/ee-data-getmapid)

    - construct a separate url for tiles for each date,
      and one to return a list of dates

    eg.
    ../tiles/hii/ -> available dates
    ../tiles/hii/2000-12-31/z/x/y/ -> 2000 tiles
    ../tiles/hii/2020-12-31/z/x/y/ -> 2020 tiles
    """

    def __init__(
        self,
        name: str,
        dated_assets: DatedAssets,
        viz_params: dict,
    ) -> None:

        self.mapids = None
        self.name = name
        self.dated_assets = dated_assets
        self.viz_params = viz_params
        self.dates = self.dated_assets.dates
        self.refresh_mapids()

    def refresh_mapids(self):
        self.mapids = {
            date: ee.Image(asset_id).getMapId(self.viz_params)
            for (date, asset_id) in self.dated_assets.asset_ids.items()
        }

    def make_urlpatterns(self, url_stub):
        tile_urlpatterns = [
            path(
                f"{url_stub}/{date}/<int:z>/<int:x>/<int:y>/",
                TileView.as_view(tilecollection=self, date=date),
            )
            for date in self.dates
        ]

        date_urlpattern = path(f"{url_stub}", DatesView.as_view(dates=self.dates))

        return [date_urlpattern] + tile_urlpatterns

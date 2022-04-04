import datetime
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

today = datetime.datetime.now().date().isoformat()


class EEAssets:
    """
    Base class for fetching Earth Engine assets
    """

    asset_ids: typing.Dict[str, str] = {}

    def __init__(self, asset_ids: typing.Dict[str, str]) -> None:
        self.asset_ids = asset_ids

    @classmethod
    def empty(cls):
        return cls({})

    @classmethod
    def fetch_assets(cls, asset_directory: str, adjust_date: bool = False):
        raise NotImplementedError()

    @classmethod
    def list_project_assets(cls, directory):
        try:
            assets = ee.data.listAssets({"parent": directory})["assets"]
        except ee.ee_exception.EEException:
            raise ValueError(
                f"Folder {directory} does not exist or is not a folder/image collection."
            )
        return assets


class DatedImageAssets(EEAssets):
    """
    - List Assets from a particular Earth Engine Directory
    - Filter to those with 'startTime' attribute
    - return dictionary {date:asset id}, and list of dates as string 'yyyy-mm-dd'

    - If adjust_date is True, subtracts one day from date
    - requires that ee.Initialize() has been run
    """

    dates: typing.List[str] = []

    def __init__(self, asset_ids: typing.Dict[str, str]) -> None:
        super().__init__(asset_ids)
        self.dates = list(sorted(self.asset_ids.keys()))

    @classmethod
    def fetch_assets(cls, asset_directory: str, adjust_date: bool = False):
        assets = cls.list_project_assets(asset_directory)

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


class FCTileAssets(EEAssets):
    """
    Earth Engine asset class for working with a single FeatureCollection
    """

    def __init__(self, asset_id: str) -> None:
        super().__init__({today: asset_id})

    @classmethod
    def fetch_assets(cls, asset_id: str, adjust_date: bool = False):
        return cls(asset_id)


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

    def __init__(self, tilecollection=None, date=None):
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


class TileCollection:
    """
    Base class for generating mapids and url patterns based on Earth Engine assets
    """

    def __init__(self, name: str, assets: EEAssets, viz_params: dict) -> None:
        self.mapids = None
        self.name = name
        self.assets = assets
        self.viz_params = viz_params

    def refresh_mapids(self):
        raise NotImplementedError()

    def make_urlpatterns(self, url_stub):
        raise NotImplementedError()


class DatedTileCollection(TileCollection):
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

    def __init__(self, name: str, assets: DatedImageAssets, viz_params: dict) -> None:
        super().__init__(name, assets, viz_params)
        self.dates = self.assets.dates
        self.refresh_mapids()

    def refresh_mapids(self):
        self.mapids = {
            date: ee.Image(asset_id).getMapId(self.viz_params)
            for (date, asset_id) in self.assets.asset_ids.items()
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


class FCTileCollection(TileCollection):
    """
    TileCollection for tiles based on a single FeatureCollection
    """

    def __init__(
        self,
        name: str,
        assets: FCTileAssets,
        viz_params: dict,
        color: [str, int],
        filters=[],
    ) -> None:
        super().__init__(name, assets, viz_params)
        self.color = color
        self.filters = filters
        self.refresh_mapids()

    def refresh_mapids(self):
        asset_id = [asset_id for (date, asset_id) in self.assets.asset_ids.items()][0]
        fc = ee.FeatureCollection(asset_id)
        for filter in self.filters:
            fc = fc.filter(filter)
        fc_image = ee.Image().byte().paint(featureCollection=fc, color=self.color)
        self.mapids = {today: fc_image.getMapId(self.viz_params)}

    def make_urlpatterns(self, url_stub):
        return [
            path(
                f"{url_stub}/<int:z>/<int:x>/<int:y>/",
                TileView.as_view(tilecollection=self, date=today),
            )
        ]

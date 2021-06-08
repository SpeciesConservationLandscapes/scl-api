from django.urls import path
from rest_framework import routers

from .resources.species import SpeciesViewSet
from .resources.scl_stats import SCLStatsViewSet
from .resources.fragment_stats import FragmentStatsViewSet
from .resources.restorationls_stats import RestorationStatsViewSet
from .resources.surveyls_stats import SurveyStatsViewSet
from .resources.me import MeViewSet
from .resources import tiles
from .resources.records import RecordsViewSet
from .reports.views import SpeciesReportView

router = routers.DefaultRouter()

me_get = MeViewSet.as_view({"get": "list"})
species_report_get = SpeciesReportView.as_view()


router.register(r"species", SpeciesViewSet, "species")
router.register(r"sclstats", SCLStatsViewSet, "sclstats")
router.register(r"fragmentstats", FragmentStatsViewSet, "fragmentstats")
router.register(r"restorationls_stats", RestorationStatsViewSet, "restorationls_stats")
router.register(r"surveyls_stats", SurveyStatsViewSet, "surveyls_stats")

tile_urls = [
    path("me/", me_get, name="me-list"),
    path("reports/species/", species_report_get, name="species-report-list"),
    path(
        "tiles/biomes/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="biomes")
    ),
    path("tiles/pas/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="pas")),
    path("tiles/kbas/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="kbas")),
    path("tiles/hii/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="hii")),
    path(
        "tiles/species/<str:species>/structural_habitat/<int:z>/<int:x>/<int:y>/",
        tiles.TileView.as_view(layer="structural_habitat"),
    ),
    path(
        "tiles/species/<str:species>/<int:z>/<int:x>/<int:y>/",
        tiles.TileView.as_view(layer="aoi"),
    ),
]

router.register(r"records", RecordsViewSet, "records")

api_urls = router.urls + tile_urls

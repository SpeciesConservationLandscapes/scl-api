from django.urls import path
from rest_framework import routers

from .resources.species import SpeciesViewSet
from .resources.scl_stats import SCLStatsViewSet
from .resources.fragment_stats import FragmentStatsViewSet
from .resources.restorationls_stats import RestorationStatsViewSet
from .resources.surveyls_stats import SurveyStatsViewSet
from .resources.me import MeViewSet
from .resources import tiles

router = routers.DefaultRouter()

me_get = MeViewSet.as_view({
    "get": "list"
})


router.register(r"species", SpeciesViewSet, "species")
router.register(r"sclstats", SCLStatsViewSet, "sclstats")
router.register(r"fragmentstats", FragmentStatsViewSet, "fragmentstats")
router.register(r"restorationls_stats", RestorationStatsViewSet, "restorationls_stats")
router.register(r"surveyls_stats", SurveyStatsViewSet, "surveyls_stats")

tile_urls = [
    path("me/", me_get, name="me-list"),
    path(
        "tiles/biomes/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="biomes")
    ),
    path("tiles/pas/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="pas")),
    path("tiles/hii/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="hii")),
    path(
        "tiles/species/<str:species>/<int:z>/<int:x>/<int:y>/",
        tiles.TileView.as_view(layer="species"),
    ),
]

api_urls = router.urls + tile_urls

from django.urls import path
from rest_framework import routers

from .resources.species import SpeciesViewSet
from .resources.scl_stats import SCLStatsViewSet
# from .resources.fragment_stats import FragmentStatsViewSet
from .resources.restorationls_stats import RestorationStatsViewSet
from .resources.surveyls_stats import SurveyStatsViewSet
from .resources.tileviews import hii_tiles_purple, hii_tiles_rainbow
from .reports.views import SpeciesReportView

router = routers.DefaultRouter()


router.register(r"species", SpeciesViewSet, "species")
router.register(r"sclstats", SCLStatsViewSet, "sclstats")
# router.register(r"fragmentstats", FragmentStatsViewSet, "fragmentstats")
router.register(r"restorationls_stats", RestorationStatsViewSet, "restorationls_stats")
router.register(r"surveyls_stats", SurveyStatsViewSet, "surveyls_stats")

# TODO: refactor
#     path(
#         "tiles/biomes/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="biomes")
#     ),
#     path("tiles/pas/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="pas")),
#     path("tiles/kbas/<int:z>/<int:x>/<int:y>/", tiles.TileView.as_view(layer="kbas")),
#     path(
#         "tiles/species/<str:species>/structural_habitat/<int:z>/<int:x>/<int:y>/",
#         tiles.TileView.as_view(layer="structural_habitat"),
#     ),
#     path(
#         "tiles/species/<str:species>/<int:z>/<int:x>/<int:y>/",
#         tiles.TileView.as_view(layer="aoi"),
#     ),

hii_urlpatterns = hii_tiles_purple.make_urlpatterns(
    "tiles/hii"
) + hii_tiles_rainbow.make_urlpatterns("tiles/hii")

api_urls = (
    router.urls
    + [
        path("reports/species/", SpeciesReportView.as_view(), name="species-report-list"),
    ]
    + hii_urlpatterns
)

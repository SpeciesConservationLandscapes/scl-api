from django.urls import path
from rest_framework import routers

from .reports.views import SpeciesReportView, GlobalReportView
from .resources.fragment_stats import (
    RestorationFragmentStatsViewSet,
    SpeciesFragmentStatsViewSet,
    SurveyFragmentStatsViewSet,
)
from .resources.indigenous_stats import IndigenousRangeStatsViewSet
from .resources.restorationls_stats import RestorationStatsViewSet
from .resources.scl_stats import SCLStatsViewSet
from .resources.species import SpeciesViewSet
from .resources.surveyls_stats import SurveyStatsViewSet
from .resources.tileviews import (
    hii_tiles_purple,
    hii_tiles_rainbow,
    biometiles,
    patiles,
    kbatiles,
    structuralhabitattiles
)

router = routers.DefaultRouter()


router.register(
    r"indigenousrangestats", IndigenousRangeStatsViewSet, "indigenousrangestats"
)
router.register(r"species", SpeciesViewSet, "species")
router.register(r"restorationls_stats", RestorationStatsViewSet, "restorationls_stats")
router.register(r"sclstats", SCLStatsViewSet, "sclstats")
router.register(r"surveyls_stats", SurveyStatsViewSet, "surveyls_stats")
router.register(
    r"restorationfragmentstats",
    RestorationFragmentStatsViewSet,
    "restorationfragmentstats",
)
router.register(
    r"speciesfragmentstats", SpeciesFragmentStatsViewSet, "speciesfragmentstats"
)
router.register(
    r"surveyfragmentstats", SurveyFragmentStatsViewSet, "surveyfragmentstats"
)

tile_urlpatterns = (
    hii_tiles_purple.make_urlpatterns("tiles/hii")
    + hii_tiles_rainbow.make_urlpatterns("tiles/hii")
    + biometiles.make_urlpatterns("tiles/biomes")
    + patiles.make_urlpatterns("tiles/pas")
    + kbatiles.make_urlpatterns("tiles/kbas")
    # TODO: make species dynamic
    + structuralhabitattiles.make_urlpatterns("tiles/species/Panthera_tigris/structural_habitat")
)

api_urls = (
    router.urls
    + tile_urlpatterns
    + [
        path(
            "reports/species/", SpeciesReportView.as_view(), name="species-report-list"
        ),
        path(
            "reports/species-global/", GlobalReportView.as_view(), name="species-global-report-list"
        ),
    ]
)

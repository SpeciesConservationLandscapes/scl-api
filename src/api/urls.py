from django.conf.urls import url
from rest_framework import routers

from .resources.species import SpeciesViewSet
from .resources.scl_stats import SCLStatsViewSet
from .resources.fragment_stats import FragmentStatsViewSet
from .resources.restorationls_stats import RestorationStatsViewSet
from .resources.surveyls_stats import SurveyStatsViewSet
from .resources.tiles import pas

# from .resources.tiles import PAView

router = routers.DefaultRouter()

router.register(r"species", SpeciesViewSet, "species")
router.register(r"sclstats", SCLStatsViewSet, "sclstats")
router.register(r"fragmentstats", FragmentStatsViewSet, "fragmentstats")
router.register(r"restorationls_stats", RestorationStatsViewSet, "restorationls_stats")
router.register(r"surveyls_stats", SurveyStatsViewSet, "surveyls_stats")

api_urls = router.urls
api_urls += (url(r"^tiles/pas/(?P<z>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+)/$", pas),)

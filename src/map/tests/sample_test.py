from map.urls import urlpatterns


def test_exists_urlpattern():
    assert len(urlpatterns) > 0

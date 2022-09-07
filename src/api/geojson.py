import datetime
import json
import os
from tempfile import NamedTemporaryFile

from django.http import FileResponse


class GeoJsonMixin:
    """
    Assuming json data returned by above aggregation and AggregateGeoStatsSerializer,
    override get() to convert json to geojson and return as FileResponse
    """

    MIME_TYPE = "application/geo+json"

    def get(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        country_name = serializer.data["properties"]["name"].replace(" ", "-")
        date_string = str(datetime.datetime.now().date())
        report_filename = f"{country_name}-{date_string}.geojson"

        try:
            tmp = NamedTemporaryFile(delete=False)
            with open(tmp.name, "w") as outfile:
                json.dump(serializer.data, outfile)

            geojson_file = open(tmp.name, "rb")
            response = FileResponse(geojson_file, content_type=self.MIME_TYPE)
            response["Content-Length"] = os.fstat(geojson_file.fileno()).st_size
            response["Content-Disposition"] = f'attachment; filename="{report_filename}"'

            return response
        finally:
            os.remove(tmp.name)

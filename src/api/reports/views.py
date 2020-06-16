import os
import datetime

from django.http import FileResponse
from django_countries import countries
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView

from . import species_report
from . import stats
from ..models import Species
from ..resources.base import UserCountryPermission


class SpeciesReportView(APIView):
    permission_classes = [UserCountryPermission]
    EXCEL_MIME_TYPE = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    table_data_order = [
        "conservation_landscape_stats",
        "fragment_landscape_stats",
        "restoration_landscape_stats",
        "survey_landscape_stats",
    ]

    def get_file_name(self, ext="xlsx"):
        date = str(datetime.datetime.now().date())
        return f"species-report-{date}.{ext}"

    def _parse_query_params(self, request):
        country_code = request.query_params.get("country")
        date = request.query_params.get("date")
        try:
            species_id = int(request.query_params.get("species"))
        except (TypeError, ValueError):
            species_id = None

        if not country_code:
            raise ParseError("Missing country")

        if not date:
            raise ParseError("Missing date")

        if not species_id:
            raise ParseError("Missing species")

        # Normalize date format
        try:
            date = str(datetime.date(*[int(d) for d in date.split("-")]))
        except ValueError:
            raise ParseError("Invalid date")

        return country_code, date, species_id

    def chart_table_data(self, landscape_stats):
        dates = []
        for lss in landscape_stats.values():
            dates.extend(lss.keys())

        dates = sorted(set(dates))
        table = []
        for date in dates:
            total_area = 0
            row = [date]
            for ls_type in self.table_data_order:
                lss = landscape_stats[ls_type].get(date) or dict()
                area = lss.get("habitat_area") or 0
                total_area += area
                row.append(area)
            table.append(row)
        return table

    def get_report_data(self, country_code, date, species_id):
        try:
            species = Species.objects.get(id=species_id)
            species_name = species.full_name
        except Species.DoesNotExist:
            species_name = ""
        country_name = dict(countries).get(country_code)

        landscape_stats = stats.calc_landscape_stats(country_code, date, species_id)

        table_data = []
        total_habitat_area = 0
        total_protected_area = 0
        total_percent_protected_area = None
        for landscape in self.table_data_order:
            lss = landscape_stats[landscape].get(date)
            table_data.append(
                [
                    lss.get("num_landscapes") or 0,
                    lss.get("habitat_area") or 0,
                    lss.get("percent_protected_area") or 0,
                ]
            )
            total_habitat_area += lss.get("habitat_area") or 0
            total_protected_area += lss.get("protected_area") or 0

        if total_habitat_area:
            total_percent_protected_area = float(total_protected_area) / float(
                total_habitat_area
            )

        chart_data = self.chart_table_data(landscape_stats)

        return {
            "country summary": {
                "species": species_name,
                "report_date": date,
                "country": country_name,
                "total_protected": total_percent_protected_area,
                "table_data": table_data,
            },
            "landscapes over time": {"chart_data": chart_data},
        }

    def get(self, request):
        report_path = None
        country_code, date, species_id = self._parse_query_params(request)
        data = self.get_report_data(country_code, date, species_id)

        try:
            report_path = species_report.generate(data)
            report_name = self.get_file_name()
            xl_file = open(report_path, "rb")
            response = FileResponse(xl_file, content_type=self.EXCEL_MIME_TYPE)
            response["Content-Length"] = os.fstat(xl_file.fileno()).st_size
            response["Content-Disposition"] = f'attachment; filename="{report_name}"'

            return response
        finally:
            if report_path and os.path.exists(report_path):
                os.remove(report_path)

import os
from datetime import datetime

from django.http import FileResponse, HttpResponseBadRequest
from django_countries import countries
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
        date = str(datetime.now().date())
        return f"species-report-{date}.{ext}"
    
    def _parse_query_params(self, request):
        country_code = request.query_params.get("country")
        date = request.query_params.get("date")
        try:
            species_id = int(request.query_params.get("species"))
        except (TypeError, ValueError):
            species_id = None
        
        if not country_code:
            raise HttpResponseBadRequest("Missing country")

        if not date:
            raise HttpResponseBadRequest("Missing date")
        
        if not species_id:
            raise HttpResponseBadRequest("Missing species")

        return country_code, date, species_id
    
    def get_report_data(self, country_code, date, species_id):
        try:
            species = Species.objects.get(id=species_id)
            species_name = species.full_name
        except Species.DoesNotExist:
            species_name = ""        
        landscape_stats = stats.calc_landscape_stats(country_code, date, species_id)
        country_name = dict(countries).get(country_code)
        table_data = []
        total_num_landscapes = 0
        total_habitat_area = 0
        total_protected_area = 0
        total_percent_protected_area = None

        for k in self.table_data_order:
            lss = landscape_stats[k]
            num_landscapes = lss.get("num_landscapes")
            habitat_area = lss.get("habitat_area")
            percent_protected_area = lss.get("percent_protected_area")

            total_num_landscapes += num_landscapes
            total_habitat_area += habitat_area
            total_protected_area += lss.get("protected_area")

            table_data.append([
                num_landscapes,
                habitat_area,
                percent_protected_area,
            ])
        
        if total_habitat_area:
            total_percent_protected_area = float(total_protected_area) / float(total_habitat_area)

        return {
            "species": species_name,
            "report_date": date,
            "country": country_name,
            "total_protected": total_percent_protected_area,
            "table_data": table_data,
        }

    def get(self, request):
        country_code, date, species_id = self._parse_query_params(request)
        data = self.get_report_data(country_code, date, species_id)

        try:
            report_path = species_report.generate(data)
            report_name = self.get_file_name()
            xl_file = open(report_path, "rb")
            response = FileResponse(xl_file, content_type=self.EXCEL_MIME_TYPE)
            response["Content-Length"] = os.fstat(xl_file.fileno()).st_size
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{report_name}"'

            return response

        finally:
            if report_path and os.path.exists(report_path):
                os.remove(report_path)

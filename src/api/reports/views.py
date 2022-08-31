import os
import datetime

from django.http import FileResponse, Http404
from django_countries import countries
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView

from . import species_report
from . import stats
from ..models import Species

class _ReportMixin:
    EXCEL_MIME_TYPE = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    COUNTRIES = dict(countries)

    def _parse_date(self, request):
        """return date in format yyyy-mm-dd"""
        date = request.query_params.get("date")
        if not date:
            raise ParseError("Missing date")

        # Normalize date format
        try:
            date = str(datetime.date(*[int(d) for d in date.split("-")]))
        except ValueError:
            raise ParseError("Invalid date")
        return date

    def _parse_species(self, request):
        """ return species_id """
        try:
            species_id = int(request.query_params.get("species"))
        except (TypeError, ValueError):
            species_id = None

        if not species_id:
            raise ParseError("Missing species")
        return species_id

    def _parse_country(self, request):
        """ return country_code """
        country_code = request.query_params.get("country")
        if not country_code:
            raise ParseError("Missing country")
        return country_code

    def _fetch_species(self, species_id):
        """ get species from db given id """
        try:
            species = Species.objects.get(id=species_id)
            species_name = species.full_name
            species_common_name = species.name_common
        except Species.DoesNotExist:
            return Http404(f"species {species_id} not found")
        return species_name, species_common_name

    def _fetch_country(self, country_code):
        """ get country given code """
        try:
            country_name = self.COUNTRIES[country_code]
        except KeyError:
            return Http404(f"country code {country_code} not found")
        return country_name

    def _create_report(self, date, species_id, species_name, species_common_name, country_code, country_name):
        """ fetch stats and fill excel template """
        landscape_stats = stats.calc_landscape_stats(country_code, date, species_id)
        indigenous_range = stats.calc_indigenous_range(country_code, species_id)

        report_path = None
        try:
            report_path, last_date = species_report.generate(
                landscape_stats, 
                date, 
                species_name, 
                species_common_name, 
                country_name, 
                indigenous_range, 
                self.COUNTRIES)
            report_name = f"{species_common_name}-{country_name}-report-{last_date}.xlsx"
            xl_file = open(report_path, "rb")
            response = FileResponse(xl_file, content_type=self.EXCEL_MIME_TYPE)
            response["Content-Length"] = os.fstat(xl_file.fileno()).st_size
            response["Content-Disposition"] = f'attachment; filename="{report_name}"'

            return response
        finally:
            if report_path and os.path.exists(report_path):
                os.remove(report_path)

class SpeciesReportView(_ReportMixin, APIView):


    def get(self, request):
        
        country_code = self._parse_country(request)
        species_id = self._parse_species(request)
        date = self._parse_date(request)

        species_name, species_common_name = self._fetch_species(species_id)
        country_name = self._fetch_country(country_code)

        return self._create_report(date, species_id, species_name, species_common_name, country_code, country_name)


class GlobalReportView(_ReportMixin, APIView):
    def get(self, request):
        
        country_code = None
        species_id = self._parse_species(request)
        date = self._parse_date(request)

        species_name, species_common_name = self._fetch_species(species_id)
        country_name = "Global"

        return self._create_report(date, species_id, species_name, species_common_name, country_code, country_name)

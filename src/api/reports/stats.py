from django.db.models import Count, Sum, F
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.expressions import RawSQL

from api.models import (
    RestorationStats, 
    SCLStats, 
    SurveyStats, 
    SpeciesFragmentStats, 
    RestorationFragmentStats, 
    SurveyFragmentStats,
    IndigenousRangeCountryStats,
    SCL,
    SpeciesFragmentLandscape,
    RestorationLandscape,
    RestorationFragmentLandscape,
    SurveyLandscape,
    SurveyFragmentLandscape,
)

CONSERVATION = SCL.ee_name
SPECIES_FRAGMENT = SpeciesFragmentLandscape.ee_name
SURVEY = SurveyLandscape.ee_name
SURVEY_FRAGMENT = SurveyFragmentLandscape.ee_name
RESTORATION = RestorationLandscape.ee_name
RESTORATION_FRAGMENT = RestorationFragmentLandscape.ee_name

TOTAL_OCCUPIED = "occupied"
OCCUPIED_LANDSCAPES = [
    CONSERVATION,
    SPECIES_FRAGMENT,
]

TOTAL_AVAILABLE = "available"
AVAILABLE_LANDSCAPES = [
    SURVEY,
    SURVEY_FRAGMENT,
    RESTORATION,
    RESTORATION_FRAGMENT,
]

TOTAL = "total"
ALL_LANDSCAPES = OCCUPIED_LANDSCAPES + AVAILABLE_LANDSCAPES


def _calc_summary(queryset, table_name, date_field, ee_name):

    data = queryset.values(date=F(date_field)).annotate(
            num_landscapes=Count(date_field),
            habitat_area=Sum("area"),
            landscapes=ArrayAgg(
                RawSQL(
                    f"""json_build_object(
                            'landscape_id', {table_name}.id, 
                            'habitat_area', area, 
                            'biome_areas', biome_areas, 
                            'type', '{ee_name}', 
                            'country_code', country
                        )""",
                    params=[],
                )
            ),
            protected_area=Sum(
                RawSQL(
                    """(
                SELECT sum(protected)
                FROM
                (
                    SELECT ((jsonb_array_elements(biome_areas)::jsonb)->'protected')::numeric as protected
                ) AS foo)""",
                    params=[],
                )
            ),
            biodiversity_area=Sum(
                RawSQL(
                    """(
                SELECT sum(kba_area)
                FROM
                (
                    SELECT ((jsonb_array_elements(biome_areas)::jsonb)->'kba_area')::numeric as kba_area
                ) AS foo)""",
                    params=[],
                )
            ),
        )
    formatted_data = dict()
    for i in range(len(data)):
        date_str = str(data[i]["date"])
        formatted_data[date_str] = data[i]
    return formatted_data


def transform_stats(stats):
    """
    - go from [type][date] to [date][type]
    - nulls to 0
    - areas as float
    - fill in any missing [date][type] with dict with all 0s
    - for each date, add additional summed types occupied, available, total
    """
    dates = []
    for key in ALL_LANDSCAPES:
        dates.extend(stats[key].keys())
    dates = list(sorted(set(dates)))

    new_stats = {}
    for date in dates:
        # go from [type][date] to [date][type]
        new_stats[date] = {}
        for key in ALL_LANDSCAPES:
            try:
                areas = stats[key][date]
                # areas as float, nulls to 0
                for area_type in ["habitat_area", "protected_area", "biodiversity_area"]:
                    try:
                        areas[area_type] = float(areas[area_type])
                    except TypeError:
                        areas[area_type] = 0.
                new_stats[date][key] = areas
            # fill in any missing [date][type] with dict with all 0s
            except KeyError:
                new_stats[date][key] = {
                    "landscapes": [],
                    "date": date,
                    "num_landscapes": 0,
                    "habitat_area": 0.,
                    "protected_area": 0.,
                    "biodiversity_area": 0.
                }
        
        # for each date, add additional summed types occupied, available, total
        new_stats[date][TOTAL_OCCUPIED] = {"date": date, "landscapes": [], }
        new_stats[date][TOTAL_AVAILABLE] ={"date": date, "landscapes": [], }
        new_stats[date][TOTAL] = {"date": date, "landscapes": [], }
        for key in ["num_landscapes", "habitat_area", "protected_area", "biodiversity_area"]:
            new_stats[date][TOTAL_OCCUPIED][key] = sum(new_stats[date][ls][key] for ls in OCCUPIED_LANDSCAPES)
            new_stats[date][TOTAL_AVAILABLE][key] = sum(new_stats[date][ls][key] for ls in AVAILABLE_LANDSCAPES)
            new_stats[date][TOTAL][key] = sum(new_stats[date][ls][key] for ls in [TOTAL_OCCUPIED, TOTAL_AVAILABLE])
    
    return new_stats


def calc_indigenous_range(country, species):
    """ get indigenous range for a country, or summed over all """
    if country is not None:
        filter_args = dict(species=species, country=country)

        qs = IndigenousRangeCountryStats.objects.filter(**filter_args)
        return float(qs.values("area")[0]["area"])
    else:
        filter_args = dict(species=species)

        qs = IndigenousRangeCountryStats.objects.filter(**filter_args)
        return float(qs.aggregate(sum_area=Sum("area"))["sum_area"])


def calc_landscape_stats(country, date, species):
    """ get stats for each landscape-type table """

    stats = {
        CONSERVATION: _calc_conservation_landscape_stats(country, date, species),
        SPECIES_FRAGMENT: _calc_species_fragment_landscape_stats(country, date, species),
        RESTORATION: _calc_restoration_landscape_stats(country, date, species),
        RESTORATION_FRAGMENT: _calc_restoration_fragment_landscape_stats(country, date, species),
        SURVEY: _calc_survey_landscape_stats(country, date, species),
        SURVEY_FRAGMENT: _calc_survey_fragment_landscape_stats(country, date, species),
    }
        
    return transform_stats(stats)


def _calc_conservation_landscape_stats(country, date, species):
    filter_args = dict(scl__date__lte=date, scl__species_id=species)
    if country is not None:
        filter_args["country"] = country

    qs = SCLStats.objects.filter(**filter_args)

    table_name = SCLStats._meta.db_table
    return _calc_summary(qs, table_name, date_field="scl__date", ee_name=SCL.ee_name)


def _calc_species_fragment_landscape_stats(country, date, species):
    filter_args = dict(
        species_fragment__date__lte=date, species_fragment__species_id=species
    )
    if country is not None:
        filter_args["country"] = country

    qs = SpeciesFragmentStats.objects.filter(**filter_args)

    table_name = SpeciesFragmentStats._meta.db_table
    return _calc_summary(qs, table_name, date_field="species_fragment__date", ee_name=SpeciesFragmentLandscape.ee_name)


def _calc_restoration_landscape_stats(country, date, species):
    filter_args = dict(
        restoration_landscape__date__lte=date,
        restoration_landscape__species_id=species,
    )
    if country is not None:
        filter_args["country"] = country

    qs = RestorationStats.objects.filter(**filter_args)

    table_name = RestorationStats._meta.db_table
    return _calc_summary(qs, table_name, date_field="restoration_landscape__date", ee_name=RestorationLandscape.ee_name)


def _calc_survey_landscape_stats(country, date, species):
    filter_args = dict(
        survey_landscape__date__lte=date,
        survey_landscape__species_id=species,
    )
    if country is not None:
        filter_args["country"] = country

    qs = SurveyStats.objects.filter(**filter_args)
    table_name = SurveyStats._meta.db_table
    return _calc_summary(qs, table_name, date_field="survey_landscape__date", ee_name=SurveyLandscape.ee_name)

def _calc_survey_fragment_landscape_stats(country, date, species):
    filter_args = dict(
        survey_fragment__date__lte=date, survey_fragment__species_id=species
    )
    if country is not None:
        filter_args["country"] = country

    qs = SurveyFragmentStats.objects.filter(**filter_args)
    table_name = SurveyFragmentStats._meta.db_table
    return _calc_summary(qs, table_name, date_field="survey_fragment__date", ee_name=SurveyFragmentLandscape.ee_name)

def _calc_restoration_fragment_landscape_stats(country, date, species):
    filter_args = dict(
        restoration_fragment__date__lte=date, restoration_fragment__species_id=species
    )
    if country is not None:
        filter_args["country"] = country

    qs = RestorationFragmentStats.objects.filter(**filter_args)
    table_name = RestorationFragmentStats._meta.db_table
    return _calc_summary(qs, table_name, date_field="restoration_fragment__date", ee_name=RestorationFragmentLandscape.ee_name)

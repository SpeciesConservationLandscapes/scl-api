from django.db.models import Count, Sum
from django.db.models.expressions import RawSQL

from api.models import FragmentStats, RestorationStats, SCLStats, SurveyStats


def _calc_summary(queryset, date_field):

    data = list(
        queryset.values(date_field).annotate(
            num_landscapes=Count(date_field),
            habitat_area=Sum("area"),
            protected_area=Sum(
                RawSQL(
                    """(
                SELECT sum(protected)
                FROM
                (
                    SELECT COALESCE(((jsonb_array_elements(biome_areas)::jsonb)->'protected'), 0.0)::numeric as protected
                ) AS foo)""",
                    params=[],
                )
            ),
        )
    )

    formatted_data = dict()
    for i in range(len(data)):
        try:
            percent_protected_area = data[i].get("protected_area") / data[i].get(
                "habitat_area"
            )
        except (TypeError, ValueError, ZeroDivisionError):
            percent_protected_area = None

        data[i]["percent_protected_area"] = round(percent_protected_area, 6)
        date_str = str(data[i][date_field])
        formatted_data[date_str] = data[i]

    return formatted_data


def calc_landscape_stats(country, date, species):
    return dict(
        conservation_landscape_stats=calc_conservation_landscape_stats(
            country, date, species
        ),
        fragment_landscape_stats=calc_fragment_landscape_stats(country, date, species),
        restoration_landscape_stats=calc_restoration_landscape_stats(
            country, date, species
        ),
        survey_landscape_stats=calc_survey_landscape_stats(country, date, species),
    )


def calc_conservation_landscape_stats(country, date, species):
    filter_args = dict(scl__date__lte=date, scl__species_id=species, country=country)

    qs = SCLStats.objects.filter(**filter_args)
    return _calc_summary(qs, date_field="scl__date")


def calc_fragment_landscape_stats(country, date, species):
    filter_args = dict(
        fragment__date__lte=date, fragment__species_id=species, country=country
    )

    qs = FragmentStats.objects.filter(**filter_args)
    return _calc_summary(qs, date_field="fragment__date")


def calc_restoration_landscape_stats(country, date, species):
    filter_args = dict(
        restoration_landscape__date__lte=date,
        restoration_landscape__species_id=species,
        country=country,
    )

    qs = RestorationStats.objects.filter(**filter_args)
    return _calc_summary(qs, date_field="restoration_landscape__date")


def calc_survey_landscape_stats(country, date, species):
    filter_args = dict(
        survey_landscape__date__lte=date,
        survey_landscape__species_id=species,
        country=country,
    )

    qs = SurveyStats.objects.filter(**filter_args)
    return _calc_summary(qs, date_field="survey_landscape__date")

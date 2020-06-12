from api.models import FragmentStats, RestorationStats, SCLStats, SurveyStats


def _calc_summary(data):
    num_landscapes = 0
    habitat_area = 0
    protected_area = 0

    for rec in data:
        num_landscapes += 1
        habitat_area += rec.area
        biome_areas = rec.biome_areas or []
        protected_area += sum([ba.get("protected") or 0 for ba in biome_areas])

    try:
        percent_protected_area = float(protected_area) / float(habitat_area)
    except (TypeError, ValueError, ZeroDivisionError):
        percent_protected_area = None

    return dict(
        num_landscapes=num_landscapes,
        habitat_area=habitat_area,
        protected_area=protected_area,
        percent_protected_area=percent_protected_area,
    )


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
    filter_args = dict(scl__date=date, scl__species_id=species, country=country)

    qs = SCLStats.objects.filter(**filter_args)
    return _calc_summary(qs)


def calc_fragment_landscape_stats(country, date, species):
    filter_args = dict(
        fragment__date=date, fragment__species_id=species, country=country
    )

    qs = FragmentStats.objects.filter(**filter_args)
    return _calc_summary(qs)


def calc_restoration_landscape_stats(country, date, species):
    filter_args = dict(
        restoration_landscape__date=date,
        restoration_landscape__species_id=species,
        country=country,
    )

    qs = RestorationStats.objects.filter(**filter_args)
    return _calc_summary(qs)


def calc_survey_landscape_stats(country, date, species):
    filter_args = dict(
        survey_landscape__date=date,
        survey_landscape__species_id=species,
        country=country,
    )

    qs = SurveyStats.objects.filter(**filter_args)
    return _calc_summary(qs)

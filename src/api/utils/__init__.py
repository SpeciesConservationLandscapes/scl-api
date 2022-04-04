import numbers
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError


def get_or_create_safeish(model_cls, **kwargs):
    try:
        return model_cls.objects.get(**kwargs), False
    except ObjectDoesNotExist:
        try:
            return model_cls.objects.create(**kwargs), True
        except IntegrityError:
            return get_or_create_safeish(model_cls, **kwargs)


def round_recursive(thing, digits):
    if isinstance(thing, dict):
        return type(thing)((key, round_recursive(value, digits)) for key, value in thing.items())
    if isinstance(thing, list):
        return type(thing)(round_recursive(value, digits) for value in thing)
    if isinstance(thing, numbers.Number):
        return round(thing, digits)
    return thing

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

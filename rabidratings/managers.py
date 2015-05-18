import sys

from django import VERSION
from django.db import models, IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.utils import six

if VERSION >= (1, 8):
    from django.db.models.fields.related import ForeignObjectRel
else:
    from django.db.models.related import RelatedObject as ForeignObjectRel
    ForeignObjectRel.related_model = property(lambda self: self.model)

from rabidratings.utils import import_module_member
from rabidratings.utils.transaction import atomic
from rabidratings.conf import RABIDRATINGS_GET_OBJECT_FUNC


def get_object(model, **kwargs):
    '''
    Return object processed from settings load function if set
    or used get from default manager
    '''
    if RABIDRATINGS_GET_OBJECT_FUNC:
        func = get_object.cache.get("get_obj_func", None)
        if not func:
            func = import_module_member(RABIDRATINGS_GET_OBJECT_FUNC)
            get_object.cache["get_obj_func"] = func
        obj = func(model, **kwargs)
    else:
        obj = model._default_manager.get(**kwargs)
    return obj
get_object.cache = {}


def get_or_create(model, manager, commit=True, **kwargs):
    assert kwargs, \
                'get_or_create() must be passed at least one keyword argument'
    defaults = kwargs.pop('defaults', {})
    lookup = kwargs.copy()
    for f in model._meta.fields:
        if f.attname in lookup:
            lookup[f.name] = lookup.pop(f.attname)
    try:
        return get_object(model, **lookup), False
    except model.DoesNotExist:
        try:
            params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
            params.update(defaults)
            obj = model(**params)
            if commit:
                with atomic(using=manager.db):
                    obj.save(force_insert=True)
            return obj, True
        except IntegrityError:
            exc_info = sys.exc_info()
            try:
                return get_object(model, **lookup), False
            except model.DoesNotExist:
                # Re-raise the DatabaseError with its original traceback.
                six.reraise(*exc_info)


class BaseRatingManager(models.Manager):

    def get_or_create(self, commit=True, **kwargs):
        return get_or_create(self.model, self, commit, **kwargs)

    def get_object(self, *args, **kwargs):
        return get_object(self.model, **kwargs)

    def get_for_object(self, obj, create_if_not=True, **kwargs):
        ct = ContentType.objects.get_for_model(obj.__class__)
        kwargs.update({
                       'target_ct': ct,
                       'target_id': obj.id,
                       })
        if create_if_not:
            return self.get_or_create(**kwargs)[0]
        return self.get_object(**kwargs)


def _get_subclasses(model):
    subclasses = [model]
    for f in model._meta.get_all_field_names():
        field = model._meta.get_field_by_name(f)[0]
        if (isinstance(field, ForeignObjectRel) and
            getattr(field.field.rel, "parent_link", None)):
            subclasses.extend(_get_subclasses(field.related_model))
    return subclasses

from django.db import models
from django.db.models.related import RelatedObject
from django.contrib.contenttypes.models import ContentType

from rabidratings.utils import import_module_member
from rabidratings.conf import RABIDRATINGS_GET_OBJECT_FUNC


def get_object(model, **kwargs):
    '''
    Return object processed from settings load function if set
    or used get from default manager
    '''
    modstr = RABIDRATINGS_GET_OBJECT_FUNC
    if modstr:
        obj = import_module_member(modstr)(model, **kwargs)
    else:
        obj = model._default_manager.get(**kwargs)
    return obj


def get_or_create(model, commit=True, **kwargs):
    created = False
    try:
        obj = get_object(model, **kwargs)
    except model.DoesNotExist:
        obj = model(**kwargs)
        created = True
        if commit:
            obj.save()
    return (obj, created)


class BaseRatingManager(models.Manager):

    def get_or_create(self, commit=True, **kwargs):
        return get_or_create(self.model, commit, **kwargs)

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
        if (isinstance(field, RelatedObject) and
            getattr(field.field.rel, "parent_link", None)):
            subclasses.extend(_get_subclasses(field.model))
    return subclasses

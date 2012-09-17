from django.db.models.related import RelatedObject

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


def _get_subclasses(model):
    subclasses = [model]
    for f in model._meta.get_all_field_names():
        field = model._meta.get_field_by_name(f)[0]
        if (isinstance(field, RelatedObject) and
            getattr(field.field.rel, "parent_link", None)):
            subclasses.extend(_get_subclasses(field.model))
    return subclasses

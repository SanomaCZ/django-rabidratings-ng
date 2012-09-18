from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from rabidratings.utils.views import HttpResponseJson


def import_module_member(modstr):
    try:
        mod_path, attr = modstr.rsplit('.', 1)
        mod = import_module(mod_path)
        member = getattr(mod, attr)
    except (AttributeError, ImportError, ValueError) as e:
        raise ImproperlyConfigured('Error importing %s: "%s"' % (modstr, e))
    else:
        return member


def get_natural_key(model_class):
    app_label = model_class._meta.app_label
    return '%s.%s' % (app_label, model_class.__name__.lower())

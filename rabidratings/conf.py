from django.conf import settings

# Settings can be overridden in the main settings file.

RABIDRATINGS_STATIC_URL = settings.STATIC_URL + 'rabidratings/'
# Virtual path to the root of the static files needed by this app.
RABIDRATINGS_STATIC_URL = getattr(settings, 'RABIDRATINGS_STATIC_URL', RABIDRATINGS_STATIC_URL)

# path to your custom function of getting object (useful for using func with cache logic)
RABIDRATINGS_GET_OBJECT_FUNC = getattr(settings, 'RABIDRATINGS_GET_OBJECT_FUNC', None)

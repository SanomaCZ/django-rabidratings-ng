from django.conf import settings

# Settings can be overridden in the main settings file.

# Virtual path to the root of the static files needed by this app.
RABIDRATINGS_STATIC_URL = getattr(settings, 'RABIDRATINGS_STATIC_URL', settings.STATIC_URL + 'rabidratings/')

# path to your custom function of getting object (useful for using func with cache logic)
RABIDRATINGS_GET_OBJECT_FUNC = getattr(settings, 'RABIDRATINGS_GET_OBJECT_FUNC', None)

# set if you want enable creating rating obj
# for spec models in RABIDRATINGS_CTS_FOR_CREATE_RATING by post save signal
RABIDRATINGS_ENABLE_CREATE_RATING_ON_SIGNAL = getattr(settings, 'RABIDRATINGS_ENABLE_CREATE_RATING_ON_SIGNAL', False)

# Spec models in natural key form for models you want created rating by post save signal
# this is used in management command for creating ratings for exist objects too
RABIDRATINGS_CTS_FOR_CREATE_RATING = getattr(settings, 'RABIDRATINGS_CTS_FOR_CREATE_RATING', ())

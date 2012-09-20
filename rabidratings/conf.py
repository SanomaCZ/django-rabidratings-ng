from django.conf import settings
from django.utils.translation import ugettext_lazy as _

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

RABIDRATINGS_TIME_DELETE_OLD_RATINGS = getattr(settings, 'RABIDRATINGS_TIME_DELETE_OLD_RATINGS', 60 * 60 * 24 * 365)

# verval values for RatingEvent model numerical value
RATING_VERBAL_VALUES = {
    20: _('Very bad'),
    40: _('Not much'),
    60: _('Average'),
    80: _('Good'),
    100: _('Excellent'),
}

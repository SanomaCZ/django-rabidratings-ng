#
# Copyright 2008 Darrel Herbst
#
# This file is part of Django-Rabid-Ratings.
#
# Django-Rabid-Ratings is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Django-Rabid-Ratings is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Django-Rabid-Ratings.  If not, see <http://www.gnu.org/licenses/>.
#
from django import template
from django.contrib.contenttypes.models import ContentType

from rabidratings.conf import RABIDRATINGS_MEDIA_URL
from rabidratings.models import Rating, RatingEvent

register = template.Library()


@register.inclusion_tag("rabidratings/rating.html", takes_context=True)
def show_rating(context, obj):
    """ Displays necessary html for the rating. """

    request = context.get('request', None)
    if not request:
        return {}

    ct = ContentType.objects.get_for_model(obj)
    rating = Rating.objects.get_or_create(target_ct=ct, target_id=obj.id)[0]
    user_rating = 0
    try:
        data = dict(target_ct=ct, target_id=obj.id, ip=request.META['REMOTE_ADDR'], user=None)
        if request.user.is_authenticated():
            data.update({'user': request.user})
        rating_event = RatingEvent.objects.get(**data)
    except RatingEvent.DoesNotExist:
        pass
    else:
        user_rating = rating_event.starts_value
    return {
        'rating_key': rating.key,
        'total_votes': rating.total_votes,
        'total_ratings': rating.total_rating,
        'rating': rating.avg_rating,
        'percent': rating.percent,
        'max_stars': 5,
        'user_rating': user_rating,
        }


@register.inclusion_tag("rabidratings/rating_header.html", takes_context=True)
def rating_header(context):
    """ Inserts necessary includes into the html. """
    return {
            'rabidratings_media_url': RABIDRATINGS_MEDIA_URL,
            'verbal_values': RatingEvent.VERBAL_VALUES,
            }

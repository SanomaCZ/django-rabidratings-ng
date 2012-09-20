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
import logging

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.transaction import commit_manually
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect

from rabidratings.utils import HttpResponseJson
from rabidratings.models import Rating, RatingEvent


logger = logging.getLogger(__name__)


@csrf_protect
@require_POST
@commit_manually
def record_vote(request):
    """
    Records the vote - note, we drop down and need to commit this transaction
    manually since we need to read, compute, and then write a new value.
    This will not work with mysql ISAM tables, so if you are using mysql, it is
    highly recommended to change this table to InnoDB to support transactions using
    the following:
       alter table rabidratings_rating engine=innodb;
    """
    logger.debug(request)
    try:
        ct_id, obj_id = Rating.split_key(request.POST['id'])
        ct = ContentType.objects.get_for_id(ct_id)

        # lookup for model RatingEvent
        lookup = dict(target_ct=ct, target_id=obj_id)
        if request.user and request.user.is_authenticated():
            lookup['user'] = request.user
        else:
            lookup['ip'] = request.META['REMOTE_ADDR']

        event, created = RatingEvent.objects.get_or_create(commit=False, **lookup)
        event.value = int(float(request.POST['vote']))
        event.save()

        rating, created = Rating.objects.get_or_create(commit=False, target_ct=ct, target_id=obj_id)

        result = dict(
            code=200,
            total_votes=rating.total_votes,
            text=render_to_string('rabidratings/rating_result_text.html', {'event': event}),
            avg_rating=render_to_string('rabidratings/avg_rating_vaule.html', {'value': rating.avg_rating})
        )

    except Exception as e:
        transaction.rollback()
        logger.debug(e)
        raise e
    else:
        transaction.commit()

    logger.debug(result)
    return HttpResponseJson(result)

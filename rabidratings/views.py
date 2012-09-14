# -*- coding: utf-8 -*-
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

from django.utils.translation import ugettext_lazy as _
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
    result = dict()
    try:
        key = request.POST['id']
        ip = request.META['REMOTE_ADDR']
        ct_id, obj_id = Rating.split_key(key)
        ct = ContentType.objects.filter(id=ct_id).get()

        rating = Rating.objects.get_or_create(target_ct=ct, target_id=obj_id)[0]
        # data for model RatingEvent
        data = dict(target_ct=ct, target_id=obj_id, ip=ip, user=None)
        # other authenticated vote from same IP is new event
        if request.user and request.user.is_authenticated():
            data.update({'user': request.user})
        event, newevent = RatingEvent.objects.get_or_create(**data)
        if not newevent:
            event.is_changing = True
            event.old_value = event.value

        event.value = int(float(request.POST['vote']))
        rating.add_rating(event)
        rating.save()
        event.save()
        result_text = render_to_string('rabidratings/rating_result_text.html', {'event': event})
        result['code'] = 200
        result['text'] = result_text
        result['avg_rating'] = str(rating.avg_rating)
        result['total_votes'] = rating.total_votes
    except Exception as e:
        transaction.rollback()
        logger.debug(e)
        result['code'] = 500
        result['error'] = _('I can not save your rating, please try again later')
        raise e
    else:
        transaction.commit()

    logger.debug(result)
    return HttpResponseJson(result)

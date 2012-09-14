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
from decimal import Decimal

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from rabidratings.utils import _get_subclasses


class Rating(models.Model):
    """
    This holds the rating value for whichever key you assign.

    Note, instead of using the database to compute the average, since we want to
    work on Google App Engine, update the counters as an event is added.

    Always use the following to get the Rating object:
       rating, created = Rating.objects.get_or_create(target_ct=ct, target_id=obj_id)
    """
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.IntegerField(_('Target ID'), db_index=True)
    target = GenericForeignKey(ct_field="target_ct", fk_field="target_id")

    total_rating = models.IntegerField(verbose_name=_('Total Rating Sum (computed)'), default=0)
    total_votes = models.IntegerField(verbose_name=_('Total Votes (computed)'), default=0)
    avg_rating = models.DecimalField(verbose_name=_('Average Rating (computed)'), default="0.0", max_digits=2, decimal_places=1)
    percent = models.FloatField(verbose_name=_('Percent Fill (computed)'), default=0.0)

    class Meta:
        unique_together = (('target_ct', 'target_id'),)
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')

    @property
    def key(self):
        return "%s_%s" % (self.target_ct_id, self.target_id)

    @staticmethod
    def split_key(key):
        ct_id, obj_id = key.split("_")
        return (ct_id, obj_id)

    @key.setter
    def key(self, val):
        ct_id, obj_id = self.__class__.split_key(val)
        self.target_ct_id = ct_id
        self.target_id = obj_id

    def __unicode__(self):
        """ Used to identify the object in admin forms. """
        return unicode(self.target)

    def add_rating(self, event):
        """
        Adds the given RatingEvent to the key.
        The event will tell you if you need to revise the counter values because
        the user is updating their vote versus adding a new vote.

        After calling add_rating the caller should save the rating but it is
        important the caller do the following three steps in a transaction, otherwise
        a race condition could occur:

        1. get the Rating object
        2. rating.add_rating(event)
        3. rating.save()

        """

        if event.is_changing:
            # the user decided to change their vote, so take away the old value first
            self.total_rating = self.total_rating - event.old_value
            self.total_votes = self.total_votes - 1

        self.total_rating = self.total_rating + event.value
        self.total_votes = self.total_votes + 1

        self.avg_rating = Decimal(str(float(self.total_rating) / float(self.total_votes) / 20.0))
        self.percent = float(self.avg_rating) / 5.0


class RatingEvent(models.Model):
    """
    Each time someone votes, the vote will be recorded by ip address.
    Yes, this is not optimal for proxies, but good enough because if you
    are behind a proxy you should be working, and not rating stuff.
    """
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.IntegerField(_('Target ID'), db_index=True)
    target = GenericForeignKey(ct_field="target_ct", fk_field="target_id")

    ip = models.IPAddressField(_('IP address'))
    user = models.ForeignKey(User, db_index=True, blank=True, null=True, verbose_name=_('User who has rated'))
    created = models.DateTimeField(_('Date of created'), auto_now_add=True)
    updated = models.DateTimeField(_('Date of last updated'), auto_now=True)
    value = models.IntegerField(_('Value'), default=0)

    # verval values for model numerical value
    VERBAL_VALUES = {
       20: _('Very bad'),
       40: _('Not much'),
       60: _('Average'),
       80: _('Good'),
       100: _('Excellent'),
    }

    class Meta:
        unique_together = (('target_ct', 'target_id', 'ip', 'user'),)
        verbose_name = _('Rating event')
        verbose_name_plural = _('Rating events')

    def __init__(self, *args, **kwargs):
        """ A vote is from one ip address - and then it can be changed. """
        super(RatingEvent, self).__init__(*args, **kwargs)

        self.is_changing = False

    def __unicode__(self):
        """ Used to identify the object in admin forms. """
        return unicode(self.target)

    @property
    def stars_value(self):
        """
        Returns value represen in range 1 - 5.
        """
        return self.value / 20

    @property
    def verbal_value(self):
        """
        Returns verbal value of value attr.
        """
        return self.VERBAL_VALUES.get(self.value, '')


def by_rating(self, extra_order_by_field_str=''):
    opts = self.model._meta
    target_id_field = '%s.%s' % (opts.db_table, opts.pk.attname)

    str_cts = "(%s)" % (", ".join([str(ContentType.objects.get_for_model(m).id) for m in _get_subclasses(self.model)]),)
    if not extra_order_by_field_str:
        extra_order_by_field_str = target_id_field
    else:
        extra_order_by_field_str = "%s.%s" % (opts.db_table, extra_order_by_field_str)
    return self.extra(
        tables=['rabidratings_rating'],
        where=['rabidratings_rating.target_ct_id IN %s and rabidratings_rating.target_id = %s' % (str_cts, target_id_field)],
        params=[],
        order_by=['-rabidratings_rating.avg_rating', '%s' % extra_order_by_field_str]
    )

QuerySet.by_rating = by_rating

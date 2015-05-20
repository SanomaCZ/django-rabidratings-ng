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

from django.db import connection, models
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db.models.query import QuerySet
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now

from rabidratings import conf
from rabidratings.utils import get_natural_key
from rabidratings.utils.transaction import atomic
from rabidratings.managers import (
                                   _get_subclasses,
                                   BaseRatingManager,
                                   )

qn = connection.ops.quote_name


class BaseRating(models.Model):
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.IntegerField(_('Target ID'), db_index=True)
    target = GenericForeignKey(ct_field="target_ct", fk_field="target_id")

    created = models.DateTimeField(_('Date of created'))
    updated = models.DateTimeField(_('Date of last updated'))

    objects = BaseRatingManager()

    class Meta:
        abstract = True

    @property
    def key(self):
        return "%s_%s" % (self.target_ct_id, self.target_id)

    @staticmethod
    def split_key(key):
        ct_id, obj_id = key.split("_")
        return ct_id, obj_id

    @key.setter
    def key(self, val):
        ct_id, obj_id = self.__class__.split_key(val)
        self.target_ct_id = ct_id
        self.target_id = obj_id

    def __unicode__(self):
        """ Used to identify the object in admin forms. """
        return unicode(self.target)

    def save(self, *args, **kwargs):
        self.updated = now()
        if not self.pk:
            self.created = self.updated

        super(BaseRating, self).save(*args, **kwargs)


class Rating(BaseRating):
    """
    This holds the rating value for whichever key you assign.

    Note, instead of using the database to compute the average, since we want to
    work on Google App Engine, update the counters as an event is added.

    Always use the following to get the Rating object:
       rating, created = Rating.objects.get_or_create(target_ct=ct, target_id=obj_id)
    """
    total_rating = models.PositiveIntegerField(verbose_name=_('Total Rating Sum (computed)'), default=0)
    total_votes = models.PositiveIntegerField(verbose_name=_('Total Votes (computed)'), default=0)
    avg_rating = models.DecimalField(verbose_name=_('Average Rating (computed)'), default=Decimal("0.0"), max_digits=2, decimal_places=1)
    percent = models.FloatField(verbose_name=_('Percent Fill (computed)'), default=0.0)

    class Meta:
        unique_together = (('target_ct', 'target_id'),)
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')

    def clean(self):
        if self.avg_rating < Decimal("0.0"):
            raise ValidationError(_("Average rating can not be negative"))
        if self.percent < 0.0:
            raise ValidationError(_("Percent can not be negative"))

    def save(self, *args, **kwargs):
        try:
            self.clean()
        except ValidationError, e:
            raise IntegrityError(e.messages)

        super(Rating, self).save(*args, **kwargs)

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

        if getattr(event, 'is_changing', False) and event.old_value > 0:
            # the user decided to change their vote, so take away the old value first
            self.total_rating = self.total_rating - event.old_value
            self.total_votes -= 1

        self.total_rating = self.total_rating + event.value
        self.total_votes += 1

        self.avg_rating = Decimal(str(float(self.total_rating) / float(self.total_votes) / 20.0))
        self.percent = float(self.avg_rating) / 5.0


class RatingEvent(BaseRating):
    """
    Each time someone votes, the vote will be recorded by ip address.
    Yes, this is not optimal for proxies, but good enough because if you
    are behind a proxy you should be working, and not rating stuff.
    """
    ip = models.GenericIPAddressField(_('IP address'), null=True)
    user = models.ForeignKey(User, db_index=True, blank=True, null=True, verbose_name=_('User who has rated'))
    value = models.PositiveIntegerField(_('Value'), default=0)

    class Meta:
        unique_together = (('target_ct', 'target_id', 'user',))
        verbose_name = _('Rating event')
        verbose_name_plural = _('Rating events')

    def clean(self):
        if conf.RABIDRATINGS_DISABLE_ANONYMOUS_USERS and not self.user:
            raise ValidationError(_("User is required for rating event"))

    def save(self, *args, **kwargs):
        try:
            self.clean()
        except ValidationError, e:
            raise IntegrityError(e.messages)

        with atomic():
            if self.value > 0:
                rating, created = Rating.objects.get_or_create(False, target_ct=self.target_ct, target_id=self.target_id)

                #redundant check for save triggered outside of view (view's save saves 1 query)
                if self.pk and getattr(self, 'is_changing', None) is None:
                    self.is_changing = True
                    self.old_value = self._default_manager.get(pk=self.pk).value

                rating.add_rating(self)
                rating.save()
                self.old_value = self.value
            super(RatingEvent, self).save(*args, **kwargs)

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
        try:
            return conf.RATING_VERBAL_VALUES[self.value]
        except KeyError:
            return ""


def by_rating(self):
    '''
    Added order by rating to queryset for using in target API
    '''
    # TODO: use better way to get objects by rating (and maybe use left outer join)
    opts = self.model._meta
    target_id_field = '%s.%s' % (qn(opts.db_table), qn(opts.pk.column))

    str_cts = "(%s)" % (", ".join([str(ContentType.objects.get_for_model(m).id) for m in _get_subclasses(self.model)]),)
    rating_table = qn(Rating._meta.db_table)
    order_by = ['-%s.avg_rating' % rating_table, '-%s.total_votes' % rating_table]
    order_by.extend(self.query.order_by[:])
    return self.extra(
        tables=['%s' % rating_table],
        where=['''%(rating_table)s.target_ct_id IN %(cts)s
                    and %(rating_table)s.target_id = %(target_id)s''' % {
                                                                         'rating_table': rating_table,
                                                                         'cts': str_cts,
                                                                         'target_id': target_id_field,
                                                                         }],
        params=[],
        order_by=order_by
    )

QuerySet.by_rating = by_rating


def create_rating_for_cts(sender, **kwargs):
    '''
    Create ratings for creating objects
    whose models are spec in RABIDRATINGS_CTS_FOR_CREATE_RATING
    '''
    if (get_natural_key(sender) in conf.RABIDRATINGS_CTS_FOR_CREATE_RATING
        and kwargs.get('created', False) and not kwargs.get('raw', False)):
        instance = kwargs['instance']
        ct = ContentType.objects.get_for_model(sender)
        Rating.objects.get_or_create(target_ct=ct, target_id=instance.id)

if conf.RABIDRATINGS_ENABLE_CREATE_RATING_ON_SIGNAL:
    signals.post_save.connect(create_rating_for_cts)

from decimal import Decimal

#from django import template
from django.template import Context
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from nose import tools

from rabidratings.models import Rating, RatingEvent
from rabidratings.templatetags.rabidratings_tags import show_rating


class TestShowRating(TestCase):

    def setUp(self):
        super(TestShowRating, self).setUp()
        self.user = User.objects.create_user(username='johan', password='johan')
        self.user2 = User.objects.create_user(username='joe', password='joe')
        self.test_obj1 = User.objects.create_user(username='test_obj1')
        self.test_obj2 = User.objects.create_user(username='test_obj2')
        self.rf = RequestFactory()

    def test_show_rating_tag(self):
        self.client.login(username='johan', password='johan')
        self.rf.user = self.user
        c = Context({'request': self.rf})
        result = show_rating(c, self.test_obj1)
        template_context = {
            'rating_key': Rating.objects.all()[0].key,
            'total_votes': 0,
            'total_ratings': 0,
            'rating': Decimal("0.0"),
            'percent': 0.0,
            'max_stars': 5,
            'user_rating': 0,
            'show_parts': 'all',
            'user': self.user,
        }
        tools.assert_equals(template_context, result)
        tools.assert_equals(RatingEvent.objects.count(), 0)
        tools.assert_equals(Rating.objects.count(), 1)

    def test_show_rating_tag_for_exist_obj(self):
        ct = ContentType.objects.get_for_model(self.test_obj2.__class__)
        lookup = dict(target_ct=ct, target_id=self.test_obj2.id)
        rating = Rating.objects.get_or_create(**lookup)[0]
        data = dict(
            id=rating.key,
            vote='80'
        )
        self.client.login(username='johan', password='johan')
        self.client.post('/submit/', data)
        self.rf.user = self.user
        c = Context({'request': self.rf})
        result = show_rating(c, self.test_obj2)
        template_context = {
            'rating_key': Rating.objects.all()[0].key,
            'total_votes': 1,
            'total_ratings': 80,
            'rating': Decimal("4"),
            'percent': 0.8,
            'max_stars': 5,
            'user_rating': 4,
            'show_parts': 'all',
            'user': self.user,
        }
        tools.assert_equals(template_context, result)
        tools.assert_equals(RatingEvent.objects.count(), 1)
        tools.assert_equals(Rating.objects.count(), 1)

    def test_show_rating_tag_for_anonymous_user(self):
        user = AnonymousUser()
        self.rf.user = user
        self.rf.META = dict(REMOTE_ADDR='192.168.2.1')
        c = Context({'request': self.rf})
        result = show_rating(c, self.test_obj1)
        template_context = {
            'rating_key': Rating.objects.all()[0].key,
            'total_votes': 0,
            'total_ratings': 0,
            'rating': Decimal("0.0"),
            'percent': 0.0,
            'max_stars': 5,
            'user_rating': 0,
            'show_parts': 'all',
            'user': user,
        }
        tools.assert_equals(template_context, result)
        tools.assert_equals(RatingEvent.objects.count(), 0)
        tools.assert_equals(Rating.objects.count(), 1)

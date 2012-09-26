from decimal import Decimal
from django.template import Context
from django.contrib.auth.models import User
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
            'rating': str(Decimal("0.0")),
            'percent': 0.0,
            'max_stars': 5,
            'user_rating': 0,
            'show_parts': 'all',
            'user': self.user,
        }
        tools.assert_equals(template_context, result)
        tools.assert_equals(RatingEvent.objects.count(), 0)
        tools.assert_equals(Rating.objects.count(), 1)

import json
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.test import TestCase

from nose import tools

from rabidratings.models import Rating, RatingEvent


class TestRatingsVote(TestCase):

    def setUp(self):
        super(TestRatingsVote, self).setUp()
        self.user = User.objects.create_user(username='johan', password='johan')
        self.user2 = User.objects.create_user(username='joe', password='joe')
        self.test_obj1 = User.objects.create_user(username='test_obj1')
        self.test_obj2 = User.objects.create_user(username='test_obj2')
        ct = ContentType.objects.get_for_model(self.test_obj1.__class__)
        lookup = dict(target_ct=ct, target_id=self.test_obj1.id)
        self.rating = Rating.objects.get_or_create(**lookup)[0]

    def test_record_vote_by_user_success(self):
        data = dict(
            id=self.rating.key,
            vote='90'
        )
        self.client.login(username='johan', password='johan')
        response = self.client.post('/submit/', data)
        tools.assert_equals(200, response.status_code)
        tools.assert_equals(200, json.loads(response.content)['code'])
        tools.assert_equals(RatingEvent.objects.count(), 1)
        tools.assert_equals(Rating.objects.count(), 1)
        tools.assert_in('4.5', json.loads(response.content)['avg_rating'])

    def test_record_voteby_user_fail(self):
        data = dict(
            id=self.rating.key,
        )
        self.client.login(username='johan', password='johan')
        response = self.client.post('/submit/', data)
        tools.assert_equals(200, response.status_code)
        tools.assert_equals(500, json.loads(response.content)['code'])
        tools.assert_equals(RatingEvent.objects.count(), 0)
        tools.assert_equals(Rating.objects.count(), 1)

    def test_record_voteby_anonymous_user_fail(self):
        data = dict(
            id=self.rating.key,
            vote='80'
        )
        response = self.client.post('/submit/', data)
        tools.assert_equals(200, response.status_code)
        tools.assert_equals(500, json.loads(response.content)['code'])
        tools.assert_equals(RatingEvent.objects.count(), 0)
        tools.assert_equals(Rating.objects.count(), 1)

    def test_record_vote_by_user_for_obj_again(self):
        data = dict(
            id=self.rating.key,
            vote='90'
        )
        self.client.login(username='johan', password='johan')
        response = self.client.post('/submit/', data)
        tools.assert_equals(200, response.status_code)
        tools.assert_equals(200, json.loads(response.content)['code'])
        tools.assert_equals(RatingEvent.objects.count(), 1)
        tools.assert_equals(Rating.objects.count(), 1)
        tools.assert_equals('4.5', json.loads(response.content)['avg_rating'])

        data.update({'vote': '50'})
        response = self.client.post('/submit/', data)
        tools.assert_equals(200, response.status_code)
        tools.assert_equals(200, json.loads(response.content)['code'])
        tools.assert_equals(RatingEvent.objects.count(), 1)
        tools.assert_equals(Rating.objects.count(), 1)
        tools.assert_equals('2.5', json.loads(response.content)['avg_rating'])

    def test_record_vote_by_two_user_for_same_obj(self):
        data = dict(
            id=self.rating.key,
            vote='90'
        )
        self.client.login(username='johan', password='johan')
        response = self.client.post('/submit/', data)
        tools.assert_equals(200, response.status_code)
        tools.assert_equals(200, json.loads(response.content)['code'])
        tools.assert_equals(RatingEvent.objects.count(), 1)
        tools.assert_equals(Rating.objects.count(), 1)
        tools.assert_equals('4.5', json.loads(response.content)['avg_rating'])

        data.update({'vote': '40'})
        self.client.login(username='joe', password='joe')
        response = self.client.post('/submit/', data)
        tools.assert_equals(200, response.status_code)
        tools.assert_equals(200, json.loads(response.content)['code'])
        tools.assert_equals(RatingEvent.objects.count(), 2)
        tools.assert_equals(Rating.objects.count(), 1)
        tools.assert_equals('3.2', json.loads(response.content)['avg_rating'])

from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.test import TestCase
from django.db import IntegrityError

from nose import tools

from rabidratings.models import Rating, RatingEvent


class TestRatingModel(TestCase):

    def setUp(self):
        super(TestRatingModel, self).setUp()
        self.user = User.objects.create_user(username='johan')
        self.user2 = User.objects.create_user(username='joe')
        self.test_obj1 = User.objects.create_user(username='test_obj1')
        self.test_obj2 = User.objects.create_user(username='test_obj2')

    def test_rating_update_by_ratingevent_for_same_obj(self):
        ct = ContentType.objects.get_for_model(self.test_obj2.__class__)
        lookup = dict(target_ct=ct, target_id=self.test_obj2.id, user=self.user)
        rating_event = RatingEvent.objects.get_or_create(**lookup)[0]
        rating_event.value = 80
        rating_event.save()
        rating = Rating.objects.get_for_object(self.test_obj2)
        tools.assert_equals(rating.total_votes, 1)
        tools.assert_equals(rating.avg_rating, Decimal('4.0'))
        rating_event = RatingEvent.objects.get_or_create(**lookup)[0]
        rating_event.value = 40
        rating_event.save()
        rating = Rating.objects.get_for_object(self.test_obj2)
        tools.assert_equals(rating.total_votes, 1)
        tools.assert_equals(rating.avg_rating, Decimal('2.0'))

    def test_rating_update_by_ratingevent_for_diff_obj(self):
        ct = ContentType.objects.get_for_model(self.test_obj2.__class__)
        lookup = dict(target_ct=ct, target_id=self.test_obj2.id, user=self.user)
        rating_event = RatingEvent.objects.get_or_create(**lookup)[0]
        rating_event.value = 80
        rating_event.save()
        rating = Rating.objects.get_for_object(self.test_obj2)
        tools.assert_equals(rating.total_votes, 1)
        tools.assert_equals(rating.avg_rating, Decimal('4.0'))
        lookup = dict(target_ct=ct, target_id=self.test_obj1.id, user=self.user)
        rating_event = RatingEvent.objects.get_or_create(**lookup)[0]
        rating_event.value = 40
        rating_event.save()
        rating = Rating.objects.get_for_object(self.test_obj1)
        tools.assert_equals(rating.total_votes, 1)
        tools.assert_equals(rating.avg_rating, Decimal('2.0'))

    def test_rating_update_by_ratingevent_for_diff_users_same_obj(self):
        ct = ContentType.objects.get_for_model(self.test_obj2.__class__)
        lookup = dict(target_ct=ct, target_id=self.test_obj2.id, user=self.user)
        rating_event = RatingEvent.objects.get_or_create(**lookup)[0]
        rating_event.value = 80
        rating_event.save()
        rating = Rating.objects.get_for_object(self.test_obj2)
        tools.assert_equals(rating.total_votes, 1)
        tools.assert_equals(rating.avg_rating, Decimal('4.0'))
        lookup = dict(target_ct=ct, target_id=self.test_obj2.id, user=self.user2)
        rating_event = RatingEvent.objects.get_or_create(**lookup)[0]
        rating_event.value = 40
        rating_event.save()
        rating = Rating.objects.get_for_object(self.test_obj2)
        tools.assert_equals(rating.total_votes, 2)
        tools.assert_equals(rating.avg_rating, Decimal('3.0'))

    def test_rating_raise_integration_error_if_percent_is_negative(self):
        rating = Rating.objects.get_for_object(self.test_obj2)
        rating.percent = -50
        tools.assert_raises(IntegrityError, rating.save)

    def test_rating_raise_integration_error_if_avg_rating_is_negative(self):
        rating = Rating.objects.get_for_object(self.test_obj2)
        rating.avg_rating = Decimal("-5.5")
        tools.assert_raises(IntegrityError, rating.save)

    def test_get_rating_for_obj_created_if_not(self):
        rating = Rating.objects.get_for_object(self.test_obj2)
        tools.assert_equals(rating.target, self.test_obj2)
        tools.assert_equals(Rating.objects.count(), 1)

    def test_get_rating_for_obj(self):
        tools.assert_raises(Rating.DoesNotExist, Rating.objects.get_for_object, self.test_obj2, False)
        tools.assert_equals(Rating.objects.count(), 0)


class TestRatingEventModel(TestCase):

    def setUp(self):
        super(TestRatingEventModel, self).setUp()
        self.user1 = User.objects.create_user(username='johan')
        self.user2 = User.objects.create_user(username='jean')
        self.test_obj1 = User.objects.create_user(username='test_obj1')
        self.test_obj2 = User.objects.create_user(username='test_obj2')
        self.content_type_user = ContentType.objects.get_for_model(self.test_obj1.__class__)
        self.lookup = dict(target_ct=self.content_type_user, target_id=self.test_obj1.id, user=self.user1)

    def test_get_ratingevent_for_obj_created_if_not(self):
        ratingevent = RatingEvent.objects.get_for_object(self.test_obj1, user=self.user1)
        tools.assert_equals(ratingevent.target, self.test_obj1)
        tools.assert_equals(RatingEvent.objects.count(), 1)

    def test_get_ratingevent_for_obj(self):
        tools.assert_raises(RatingEvent.DoesNotExist, lambda: RatingEvent.objects.get_for_object(self.test_obj2, False, user=self.user1))
        tools.assert_equals(RatingEvent.objects.count(), 0)

    def test_ratingevent_throw_excpetion_if_user_is_none(self):
        lookup = self.lookup.copy()
        lookup.update({'user': None})
        tools.assert_raises(IntegrityError, lambda: RatingEvent.objects.create(**lookup))

    def test_ratingevent_unique_on_same_obj_for_user(self):
        lookup = self.lookup.copy()
        RatingEvent.objects.create(**lookup)
        tools.assert_equals(RatingEvent.objects.count(), 1)
        tools.assert_raises(IntegrityError, lambda: RatingEvent.objects.create(**lookup))

    def test_ratingevent_not_unique_on_same_obj_for_diff_users(self):
        lookup = self.lookup.copy()
        RatingEvent.objects.create(**lookup)
        tools.assert_equals(RatingEvent.objects.count(), 1)
        lookup.update({'user': self.user2})
        RatingEvent.objects.create(**lookup)
        tools.assert_equals(RatingEvent.objects.count(), 2)

    def test_ratingevent_not_unique_on_diff_objects_for_user(self):
        lookup = self.lookup.copy()
        RatingEvent.objects.create(**lookup)
        tools.assert_equals(RatingEvent.objects.count(), 1)
        lookup.update({'target_id': self.test_obj2.id})
        RatingEvent.objects.create(**lookup)
        tools.assert_equals(RatingEvent.objects.count(), 2)

    def test_ratingevent_stars_value(self):
        ratingevent = RatingEvent.objects.get_or_create(**self.lookup)[0]
        ratingevent.value = 80
        tools.assert_equals(ratingevent.stars_value, 4)

    def test_ratingevent_verbal_value_out_of(self):
        ratingevent = RatingEvent.objects.get_or_create(**self.lookup)[0]
        ratingevent.value = 30
        tools.assert_equals(ratingevent.verbal_value, '')


class TestQuerySetWithRating(TestCase):

    def setUp(self):
        super(TestQuerySetWithRating, self).setUp()
        self.user = User.objects.create_user(username='johan')
        self.test_obj1 = User.objects.create_user(username='test_obj1')
        self.test_obj2 = User.objects.create_user(username='test_obj2')
        self.test_obj3 = User.objects.create_user(username='test_obj3')

    def test_get_objects_by_rating(self):
        ct = ContentType.objects.get_for_model(self.test_obj2.__class__)
        lookup = dict(target_ct=ct, target_id=self.test_obj2.id, user=self.user)
        rating_event = RatingEvent.objects.get_or_create(**lookup)[0]
        rating_event.value = 80
        rating_event.save()
        
        ct = ContentType.objects.get_for_model(self.test_obj1.__class__)
        lookup = dict(target_ct=ct, target_id=self.test_obj1.id, user=self.user)
        rating_event = RatingEvent.objects.get_or_create(**lookup)[0]
        rating_event.value = 40
        rating_event.save()

        ct = ContentType.objects.get_for_model(self.test_obj3.__class__)
        lookup = dict(target_ct=ct, target_id=self.test_obj3.id)
        rating = Rating.objects.get_or_create(**lookup)[0]
        
        list_users = list(User.objects.filter(username__startswith='test_').by_rating())
        
        tools.assert_equals(list_users, [self.test_obj2, self.test_obj1, self.test_obj3])

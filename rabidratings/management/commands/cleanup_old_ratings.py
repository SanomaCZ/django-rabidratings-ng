from datetime import timedelta

from rabidratings.conf import RABIDRATINGS_TIME_DELETE_OLD_RATINGS
from rabidratings.models import Rating, RatingEvent

from django.core.management.base import NoArgsCommand
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now


class Command(NoArgsCommand):
    help = "Delete ratings whose last update is older than time spec in settings"

    def handle(self, **options):
        delete_date = now() - timedelta(seconds=RABIDRATINGS_TIME_DELETE_OLD_RATINGS)
        qs = Rating.objects.filter(updated__lte=delete_date)
        for rating in qs:
            RatingEvent.objects.filter(target_ct=rating.target_ct, target_id=rating.target_id).delete()

        qs.delete()

from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = "Delete ratings whose last update is older than time spec in settings"

    def handle(self, **options):
        from datetime import datetime, timedelta
        from rabidratings.conf import RABIDRATINGS_TIME_DELETE_OLD_RATINGS
        from rabidratings.models import Rating, RatingEvent

        delete_date = datetime.now() - timedelta(seconds=RABIDRATINGS_TIME_DELETE_OLD_RATINGS)
        for rating in Rating.objects.filter(updated__lte=delete_date):
            RatingEvent.objects.filter(target_ct=rating.target_ct, target_id=rating.target_id).delete()
            rating.delete()

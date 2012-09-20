from django.core.management.base import NoArgsCommand
from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType

from rabidratings.conf import RABIDRATINGS_CTS_FOR_CREATE_RATING
from rabidratings.models import Rating


class Command(NoArgsCommand):
    help = """Create ratings for objects that are in db
              and whose models (as natural keys) are in setings"""

    def handle(self, **options):
        for natural_key in RABIDRATINGS_CTS_FOR_CREATE_RATING:
            model = get_model(*natural_key.split("."))
            ct = ContentType.objects.get_by_natural_key(*natural_key.split("."))
            ids = tuple(rating.target_id for rating in Rating.objects.filter(target_ct=ct))
            for obj in model.objects.exclude(id__in=ids):
                Rating.objects.create(target_ct=ct, target_id=obj.id)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '__latest__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target_id', models.IntegerField(verbose_name='Target ID', db_index=True)),
                ('created', models.DateTimeField(verbose_name='Date of created')),
                ('updated', models.DateTimeField(verbose_name='Date of last updated')),
                ('total_rating', models.PositiveIntegerField(default=0, verbose_name='Total Rating Sum (computed)')),
                ('total_votes', models.PositiveIntegerField(default=0, verbose_name='Total Votes (computed)')),
                ('avg_rating', models.DecimalField(default=Decimal('0.0'), verbose_name='Average Rating (computed)', max_digits=2, decimal_places=1)),
                ('percent', models.FloatField(default=0.0, verbose_name='Percent Fill (computed)')),
                ('target_ct', models.ForeignKey(verbose_name='Target content type', to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Rating',
                'verbose_name_plural': 'Ratings',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together=set([(b'target_ct', b'target_id')]),
        ),
        migrations.CreateModel(
            name='RatingEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target_id', models.IntegerField(verbose_name='Target ID', db_index=True)),
                ('created', models.DateTimeField(verbose_name='Date of created')),
                ('updated', models.DateTimeField(verbose_name='Date of last updated')),
                ('ip', models.IPAddressField(null=True, verbose_name='IP address')),
                ('value', models.PositiveIntegerField(default=0, verbose_name='Value')),
                ('target_ct', models.ForeignKey(verbose_name='Target content type', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(verbose_name='User who has rated', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Rating event',
                'verbose_name_plural': 'Rating events',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='ratingevent',
            unique_together=set([(b'target_ct', b'target_id', b'user')]),
        ),
    ]

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Rating.updated'
        db.alter_column('rabidratings_rating', 'updated', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Rating.created'
        db.alter_column('rabidratings_rating', 'created', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'RatingEvent.updated'
        db.alter_column('rabidratings_ratingevent', 'updated', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'RatingEvent.created'
        db.alter_column('rabidratings_ratingevent', 'created', self.gf('django.db.models.fields.DateTimeField')())

    def backwards(self, orm):

        # Changing field 'Rating.updated'
        db.alter_column('rabidratings_rating', 'updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Changing field 'Rating.created'
        db.alter_column('rabidratings_rating', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'RatingEvent.updated'
        db.alter_column('rabidratings_ratingevent', 'updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Changing field 'RatingEvent.created'
        db.alter_column('rabidratings_ratingevent', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rabidratings.rating': {
            'Meta': {'unique_together': "(('target_ct', 'target_id'),)", 'object_name': 'Rating'},
            'avg_rating': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '2', 'decimal_places': '1'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'target_ct': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'target_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'total_rating': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'total_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        'rabidratings.ratingevent': {
            'Meta': {'unique_together': "(('target_ct', 'target_id', 'ip', 'user'),)", 'object_name': 'RatingEvent'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'target_ct': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'target_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['rabidratings']
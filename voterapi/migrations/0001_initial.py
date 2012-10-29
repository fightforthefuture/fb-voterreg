# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VoterRecord'
        db.create_table('voterapi_voterrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fb_uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('votizen_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('registered', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('voterapi', ['VoterRecord'])


    def backwards(self, orm):
        # Deleting model 'VoterRecord'
        db.delete_table('voterapi_voterrecord')


    models = {
        'voterapi.voterrecord': {
            'Meta': {'object_name': 'VoterRecord'},
            'fb_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'votizen_id': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['voterapi']
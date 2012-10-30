# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'VoterRecord.loaded_history'
        db.add_column('voterapi_voterrecord', 'loaded_history',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'VoterRecord.loaded_history'
        db.delete_column('voterapi_voterrecord', 'loaded_history')


    models = {
        'voterapi.voterrecord': {
            'Meta': {'object_name': 'VoterRecord'},
            'fb_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loaded_history': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'votizen_id': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['voterapi']
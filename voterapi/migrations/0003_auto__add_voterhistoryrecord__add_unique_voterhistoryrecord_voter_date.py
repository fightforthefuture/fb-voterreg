# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VoterHistoryRecord'
        db.create_table('voterapi_voterhistoryrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('voter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voterapi.VoterRecord'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('voted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('voterapi', ['VoterHistoryRecord'])

        # Adding unique constraint on 'VoterHistoryRecord', fields ['voter', 'date']
        db.create_unique('voterapi_voterhistoryrecord', ['voter_id', 'date'])


    def backwards(self, orm):
        # Removing unique constraint on 'VoterHistoryRecord', fields ['voter', 'date']
        db.delete_unique('voterapi_voterhistoryrecord', ['voter_id', 'date'])

        # Deleting model 'VoterHistoryRecord'
        db.delete_table('voterapi_voterhistoryrecord')


    models = {
        'voterapi.voterhistoryrecord': {
            'Meta': {'unique_together': "(('voter', 'date'),)", 'object_name': 'VoterHistoryRecord'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'voted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voterapi.VoterRecord']"})
        },
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
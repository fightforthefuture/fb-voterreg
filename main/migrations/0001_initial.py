# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'User'
        db.create_table('main_user', (
            ('fb_uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('votizen_id', self.gf('django.db.models.fields.CharField')(max_length=132, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('data_fetched', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('registered', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('date_pledged', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('friends_fetch_started', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('invited_pledge_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('wont_vote_reason', self.gf('django.db.models.fields.CharField')(max_length=18, blank=True)),
            ('used_registration_widget', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('friends_fetched', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_invited_friends', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('main', ['User'])

        # Adding model 'Friendship'
        db.create_table('main_friendship', (
            ('fb_uid', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('votizen_id', self.gf('django.db.models.fields.CharField')(max_length=132, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('user_fb_uid', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('registered', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('date_pledged', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('invited_pledge_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('wont_vote_reason', self.gf('django.db.models.fields.CharField')(max_length=18, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'])),
            ('display_ordering', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('main', ['Friendship'])

        # Adding unique constraint on 'Friendship', fields ['user', 'fb_uid']
        db.create_unique('main_friendship', ['user_id', 'fb_uid'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'User'
        db.delete_table('main_user')

        # Deleting model 'Friendship'
        db.delete_table('main_friendship')

        # Removing unique constraint on 'Friendship', fields ['user', 'fb_uid']
        db.delete_unique('main_friendship', ['user_id', 'fb_uid'])
    
    
    models = {
        'main.friendship': {
            'Meta': {'unique_together': "(('user', 'fb_uid'),)", 'object_name': 'Friendship'},
            'date_pledged': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'display_ordering': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'fb_uid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_pledge_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']"}),
            'user_fb_uid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'votizen_id': ('django.db.models.fields.CharField', [], {'max_length': '132', 'blank': 'True'}),
            'wont_vote_reason': ('django.db.models.fields.CharField', [], {'max_length': '18', 'blank': 'True'})
        },
        'main.user': {
            'Meta': {'object_name': 'User'},
            'data_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_invited_friends': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_pledged': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'fb_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'friends_fetch_started': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'friends_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_pledge_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'used_registration_widget': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'votizen_id': ('django.db.models.fields.CharField', [], {'max_length': '132', 'blank': 'True'}),
            'wont_vote_reason': ('django.db.models.fields.CharField', [], {'max_length': '18', 'blank': 'True'})
        }
    }
    
    complete_apps = ['main']

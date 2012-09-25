# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Friendship.location_name'
        db.add_column('main_friendship', 'location_name', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True), keep_default=False)

        # Adding field 'Friendship.far_from_home'
        db.add_column('main_friendship', 'far_from_home', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Friendship.birthday'
        db.add_column('main_friendship', 'birthday', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting field 'Friendship.location_name'
        db.delete_column('main_friendship', 'location_name')

        # Deleting field 'Friendship.far_from_home'
        db.delete_column('main_friendship', 'far_from_home')

        # Deleting field 'Friendship.birthday'
        db.delete_column('main_friendship', 'birthday')
    
    
    models = {
        'main.friendship': {
            'Meta': {'unique_together': "(('user', 'fb_uid'),)", 'object_name': 'Friendship'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.FriendshipBatch']", 'null': 'True'}),
            'birthday': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_pledged': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'display_ordering': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'far_from_home': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'fb_uid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_pledge_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'location_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']"}),
            'user_fb_uid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'votizen_id': ('django.db.models.fields.CharField', [], {'max_length': '132', 'blank': 'True'}),
            'wont_vote_reason': ('django.db.models.fields.CharField', [], {'max_length': '18', 'blank': 'True'})
        },
        'main.friendshipbatch': {
            'Meta': {'object_name': 'FriendshipBatch'},
            'completely_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'regular_batch_no': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']"})
        },
        'main.user': {
            'Meta': {'object_name': 'User'},
            'birthday': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'data_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_invited_friends': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_pledged': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'far_from_home': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'fb_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'friends_fetch_started': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'friends_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_pledge_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'location_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'used_registration_widget': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'votizen_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '132', 'blank': 'True'}),
            'wont_vote_reason': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '18', 'blank': 'True'})
        }
    }
    
    complete_apps = ['main']

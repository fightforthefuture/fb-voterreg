# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LastAppNotification'
        db.create_table('main_lastappnotification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'], unique=True)),
            ('pledged_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('voted_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('notification_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('main', ['LastAppNotification'])

        # Adding model 'WonBadge'
        db.create_table('main_wonbadge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.User'])),
            ('badge_type', self.gf('django.db.models.fields.IntegerField')()),
            ('num', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('message_shown', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('main', ['WonBadge'])

        # Adding unique constraint on 'WonBadge', fields ['user', 'badge_type']
        db.create_unique('main_wonbadge', ['user_id', 'badge_type'])


    def backwards(self, orm):
        # Removing unique constraint on 'WonBadge', fields ['user', 'badge_type']
        db.delete_unique('main_wonbadge', ['user_id', 'badge_type'])

        # Deleting model 'LastAppNotification'
        db.delete_table('main_lastappnotification')

        # Deleting model 'WonBadge'
        db.delete_table('main_wonbadge')


    models = {
        'main.friendship': {
            'Meta': {'unique_together': "(('user', 'fb_uid'),)", 'object_name': 'Friendship'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.FriendshipBatch']", 'null': 'True'}),
            'batch_type': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'birthday': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_pledged': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_voted': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'display_ordering': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'far_from_home': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fb_uid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_individually': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invited_pledge_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'invited_with_batch': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_random': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']"}),
            'user_fb_uid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'votizen_id': ('django.db.models.fields.CharField', [], {'max_length': '132', 'blank': 'True'}),
            'wont_vote_reason': ('django.db.models.fields.CharField', [], {'max_length': '18', 'blank': 'True'})
        },
        'main.friendshipbatch': {
            'Meta': {'object_name': 'FriendshipBatch'},
            'completely_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'regular_batch_no': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']"})
        },
        'main.lastappnotification': {
            'Meta': {'object_name': 'LastAppNotification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'pledged_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']", 'unique': 'True'}),
            'voted_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'main.mission': {
            'Meta': {'unique_together': "(('user', 'type'),)", 'object_name': 'Mission'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pledged_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']"})
        },
        'main.user': {
            'Meta': {'object_name': 'User'},
            'birthday': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'data_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_invited_friends': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_pledged': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_voted': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'explicit_share': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'explicit_share_vote': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'far_from_home': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fb_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'friends_fetch_last_activity': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'friends_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_pledge_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'location_city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'location_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'location_state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'num_friends': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unsubscribed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'used_registration_widget': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'votizen_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '132', 'blank': 'True'}),
            'wont_vote_reason': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '18', 'blank': 'True'})
        },
        'main.votingblock': {
            'Meta': {'object_name': 'VotingBlock'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'organization_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'organization_privace_policy': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'organization_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'main.votingblockmember': {
            'Meta': {'object_name': 'VotingBlockMember'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']"}),
            'voting_block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.VotingBlock']"})
        },
        'main.wonbadge': {
            'Meta': {'unique_together': "(('user', 'badge_type'),)", 'object_name': 'WonBadge'},
            'badge_type': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_shown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.User']"})
        }
    }

    complete_apps = ['main']
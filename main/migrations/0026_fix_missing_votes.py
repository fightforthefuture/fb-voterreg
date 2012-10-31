# encoding: utf-8
from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        """
        Iterates over each User, ensuring that if they have marked themselves
        as having voted, each Friendship referencing them is also updated to
        indicate that they have voted.
        """
        users = orm.User.objects.all()
        for user in users:
            if user.voted:
                try:
                    friendships_for_user = orm.Friendship.objects.filter(fb_uid=user.fb_uid)
                    for friendship in friendships_for_user:
                        friendship.date_voted = user.date_voted
                        friendship.save()
                except orm.Friendship.DoesNotExist:
                    pass

    def backwards(self, orm):
        pass

    models = {
        'main.friendship': {
            'Meta': {'unique_together': "(('user', 'fb_uid'),)", 'object_name': 'Friendship'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.FriendshipBatch']", 'null': 'True'}),
            'batch_type': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'birthday': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_pledged': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_voted': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'display_ordering': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'far_from_home': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'fb_uid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_individually': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'invited_pledge_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'invited_with_batch': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_random': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
            'data_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_invited_friends': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_pledged': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_voted': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'explicit_share': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'explicit_share_vote': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'far_from_home': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'fb_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'friends_fetch_last_activity': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'friends_fetched': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_pledge_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'location_city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'location_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'location_state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'num_friends': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'unsubscribed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'used_registration_widget': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'votizen_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '132', 'blank': 'True'}),
            'wont_vote_reason': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '18', 'blank': 'True'})
        }
    }

    complete_apps = ['main']

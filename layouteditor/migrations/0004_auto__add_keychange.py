# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'KeyChange'
        db.create_table('layouteditor_keychange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['layouteditor.Layout'])),
            ('row', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('pos', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('before', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('after', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('done', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('layouteditor', ['KeyChange'])


    def backwards(self, orm):
        # Deleting model 'KeyChange'
        db.delete_table('layouteditor_keychange')


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
        'layouteditor.keybinding': {
            'Meta': {'object_name': 'KeyBinding'},
            'char': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['layouteditor.Level']"}),
            'pos': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'row': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'layouteditor.keychange': {
            'Meta': {'object_name': 'KeyChange'},
            'after': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'before': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['layouteditor.Layout']"}),
            'pos': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'row': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'layouteditor.layout': {
            'Meta': {'unique_together': "(('owner', 'name'),)", 'object_name': 'Layout'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'ref1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ref1_using_layouts'", 'null': 'True', 'to': "orm['layouteditor.Level']"}),
            'ref2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ref2_using_layouts'", 'null': 'True', 'to': "orm['layouteditor.Level']"})
        },
        'layouteditor.level': {
            'Meta': {'unique_together': "(('layout', 'level'),)", 'object_name': 'Level'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['layouteditor.Layout']"}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'modifiers': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['layouteditor']
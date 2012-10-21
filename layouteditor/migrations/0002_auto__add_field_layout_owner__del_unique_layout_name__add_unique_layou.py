# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Use the first staff user as owner for existing layouts
        def_owner = orm['auth.User'].objects.filter(is_staff=True).order_by('id')[0].id if not db.dry_run else 1
        
        # Removing unique constraint on 'Layout', fields ['name']
        db.delete_unique('layouteditor_layout', ['name'])

        # Adding field 'Layout.owner'
        db.add_column('layouteditor_layout', 'owner', self.gf('django.db.models.fields.related.ForeignKey')(default=def_owner, to=orm['auth.User']), keep_default=False)

        # Adding unique constraint on 'Layout', fields ['owner', 'name']
        db.create_unique('layouteditor_layout', ['owner_id', 'name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Layout', fields ['owner', 'name']
        db.delete_unique('layouteditor_layout', ['owner_id', 'name'])

        # Deleting field 'Layout.owner'
        db.delete_column('layouteditor_layout', 'owner_id')

        # Adding unique constraint on 'Layout', fields ['name']
        db.create_unique('layouteditor_layout', ['name'])


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
        'layouteditor.layout': {
            'Meta': {'unique_together': "(('owner', 'name'),)", 'object_name': 'Layout'},
            'font': ('django.db.models.fields.CharField', [], {'default': "'verdana, ezra sil'", 'max_length': '80', 'null': 'True', 'blank': 'True'}),
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

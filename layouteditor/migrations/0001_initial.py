# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Layout'
        db.create_table('layouteditor_layout', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('ref1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ref1_using_layouts', null=True, to=orm['layouteditor.Level'])),
            ('ref2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ref2_using_layouts', null=True, to=orm['layouteditor.Level'])),
            ('font', self.gf('django.db.models.fields.CharField')(default='verdana, ezra sil', max_length=80, null=True, blank=True)),
        ))
        db.send_create_signal('layouteditor', ['Layout'])

        # Adding model 'Level'
        db.create_table('layouteditor_level', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['layouteditor.Layout'])),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('modifiers', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, blank=True)),
        ))
        db.send_create_signal('layouteditor', ['Level'])

        # Adding unique constraint on 'Level', fields ['layout', 'level']
        db.create_unique('layouteditor_level', ['layout_id', 'level'])

        # Adding model 'KeyBinding'
        db.create_table('layouteditor_keybinding', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['layouteditor.Level'])),
            ('row', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('pos', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('char', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('layouteditor', ['KeyBinding'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Level', fields ['layout', 'level']
        db.delete_unique('layouteditor_level', ['layout_id', 'level'])

        # Deleting model 'Layout'
        db.delete_table('layouteditor_layout')

        # Deleting model 'Level'
        db.delete_table('layouteditor_level')

        # Deleting model 'KeyBinding'
        db.delete_table('layouteditor_keybinding')


    models = {
        'layouteditor.keybinding': {
            'Meta': {'object_name': 'KeyBinding'},
            'char': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['layouteditor.Level']"}),
            'pos': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'row': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'layouteditor.layout': {
            'Meta': {'object_name': 'Layout'},
            'font': ('django.db.models.fields.CharField', [], {'default': "'verdana, ezra sil'", 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
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

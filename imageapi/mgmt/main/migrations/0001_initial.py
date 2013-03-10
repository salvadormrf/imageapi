# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Page'
        db.create_table(u'main_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('suffix', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('prefix', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'main', ['Page'])

        # Adding model 'Placeholder'
        db.create_table(u'main_placeholder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('height', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Page'])),
        ))
        db.send_create_signal(u'main', ['Placeholder'])


    def backwards(self, orm):
        # Deleting model 'Page'
        db.delete_table(u'main_page')

        # Deleting model 'Placeholder'
        db.delete_table(u'main_placeholder')


    models = {
        u'main.page': {
            'Meta': {'object_name': 'Page'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'main.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Page']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '100'})
        }
    }

    complete_apps = ['main']
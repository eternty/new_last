# -*- coding: utf-8 -*-
# Generated by Django 1.9b1 on 2015-11-17 15:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='defines_attribute',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='project.Attribute', verbose_name='Определяет_атрибут'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9b1 on 2015-11-18 12:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20151117_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='if_first',
            field=models.BooleanField(default=False),
        ),
    ]

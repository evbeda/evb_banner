# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-06 23:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banner', '0012_auto_20180405_1947'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='evb_id',
            field=models.IntegerField(default=0),
        ),
    ]

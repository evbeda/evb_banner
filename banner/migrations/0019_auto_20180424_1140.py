# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-24 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banner', '0018_event_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='custom_logo',
            field=models.FileField(max_length=500, upload_to=b'custom_logo/'),
        ),
    ]
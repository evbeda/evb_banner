from django.db import models
from django.utils import timezone


class Events(models.Model):
    event_title = models.CharField(max_length=200)
    event_description = models.TextField()
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    event_logo = models.CharField(max_length=200)
    event_organizer = models.CharField(max_length=200)
    event_custom_title = models.CharField(max_length=200)
    enven_custom_logo = models.CharField(max_length=200)
    event_custom_description = models.TextField()
    banner = models.ForeingKey(
        'models.Banner')
    event_design = models.ForeingKey('models.EventDesign')


class Banner(models.Model):
    banner_design = models.ForeignKey(
        'models.BannerDesign',
    )
    # event = models.ForeignKey(
    #     'models.Event',
    #     on_delete=models.CASCADE,
    # )
    user = models.ForeignKey('auth.User')
    banner_title = models.CharField(max_length=200)
    banner_description = models.TextField()
    created_date = models.DateTimeField(
        default=timezone.now)


class BannerDesign(models.Model):
    user = models.ForeignKey('auth.User')
    banner_design_name = models.CharField(max_length=200)
    created_date = models.DateTimeField(
        default=timezone.now)


class EventDesign(models.Model):
    event_design_user = models.ForeingKey('models.User')
    event_design_name = models.CharField(max_length=200)
    created_date = models.DateTimeField(
        default=timezone.now)

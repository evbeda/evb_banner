from factory import (
    DjangoModelFactory,
    Faker,
    Sequence,
    SubFactory,
    LazyFunction,
    lazy_attribute,
)
from . import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template.defaultfilters import slugify


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    first_name = Sequence(lambda n: "Agent%03d" % n)
    last_name = Sequence(lambda n: "Agent%03d" % n)
    username = lazy_attribute(
        lambda o: slugify(
            o.first_name + '.' + o.last_name,
        )
    )


class BannerDesignFactory(DjangoModelFactory):
    class Meta:
        model = models.BannerDesign
        django_get_or_create = ('user',)

    user = SubFactory(UserFactory)
    name = Sequence(lambda n: "BannerDesign%03d" % n)
    created = LazyFunction(timezone.now)


class BannerFactory(DjangoModelFactory):
    class Meta:
        model = models.Banner
        django_get_or_create = ('user',)

    user = SubFactory(UserFactory)
    design = SubFactory(BannerDesignFactory)
    title = Sequence(lambda n: "Banner%03d" % n)
    description = Faker('text')
    created = LazyFunction(timezone.now)


class EventDesignFactory(DjangoModelFactory):
    class Meta:
        model = models.EventDesign
        django_get_or_create = ('user',)

    user = SubFactory(UserFactory)
    name = Sequence(lambda n: "Banner%03d" % n)
    created = LazyFunction(timezone.now)


class EventFactory(DjangoModelFactory):
    class Meta:
        model = models.Event
        django_get_or_create = ('user',)

    title = Sequence(lambda n: "Event%03d" % n)
    description = Faker('text')
    start = LazyFunction(timezone.now)
    end = LazyFunction(timezone.now)
    custom_title = 'none'
    custom_logo = 'none'
    custom_description = 'none'
    created = LazyFunction(timezone.now)
    user = SubFactory(UserFactory)
    banner = SubFactory(BannerFactory)

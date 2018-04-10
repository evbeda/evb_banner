# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from unittest import skip
from .factories import (
    BannerDesignFactory,
    BannerFactory,
    EventFactory,
    UserFactory,
)
from .models import (
    Banner,
    BannerDesign,
    Event,
    EventDesign,
)

from .views import (
    BannerView,
    BannerNewEventsSelectedCreateView,
)

from mock import (
    MagicMock,
    patch,
)


class TestBase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username='testuser',
            password='12345',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        self.user.set_password('hello')
        self.user.save()
        login = self.client.login(username='testuser', password='hello')
        return login


class IndexViewTest(TestBase):

    def setUp(self):
        super(IndexViewTest, self).setUp()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_no_banners(self):
        response = self.client.get('/')
        self.assertContains(response, 'No banners yet!')


class BannerDesignTest(TestBase):

    def test_banner_design_creation(self):
        w = BannerDesignFactory()
        self.assertTrue(isinstance(w, BannerDesign))
        banner_design_list = BannerDesign.objects.all()
        banner_design = banner_design_list[len(banner_design_list) - 1]
        self.assertEqual(banner_design.name, w.name)


class BannerDesignViewTest(TestBase):

    def setUp(self):
        super(BannerDesignViewTest, self).setUp()
        self.banner = BannerFactory()

    def test_banner_design_view(self):
        response = self.client.get('/banner/' +
                                   str(self.banner.id) +
                                   '/banner_design/')
        self.assertEqual(response.status_code, 200)

    def test_events_inside_banner(self):
        event1 = EventFactory.build()
        event1.banner = self.banner
        event1.save()

        event2 = EventFactory.build()
        event2.banner = self.banner
        event2.save()

        response = self.client.get('/banner/' +
                                   str(self.banner.id) +
                                   '/banner_design/')
        self.assertContains(response, 'event-' + str(event1.id))
        self.assertContains(response, 'event-' + str(event2.id))


class BannerTest(TestBase):

    def test_banner_creation(self):
        w = BannerFactory()
        self.assertTrue(isinstance(w, Banner))
        banner_list = Banner.objects.all()
        banner = banner_list[len(banner_list) - 1]
        self.assertEqual(banner.title, w.title)

    @skip('Falta implementar banner_new!')
    def test_banner_new(self):
        design = EventDesign(user=UserFactory())
        design.save()
        ev1 = Event(
            start=timezone.now(),
            end=timezone.now(),
            design=design
        )
        ev2 = Event(
            start=timezone.now(),
            end=timezone.now(),
            design=design
        )
        events = [ev1, ev2]
        bw = BannerView()
        b = bw.banner_new(events)
        self.assertTrue(isinstance(b, Banner))
        self.assertEquals(b, ev1.banner)


class BannerDetailViewTest(TestBase):

    def setUp(self):
        super(BannerDetailViewTest, self).setUp()
        self.banner = BannerFactory()

    def test_banner_detail_view(self):
        response = self.client.get(self.banner.get_absolute_url)
        self.assertEqual(response.status_code, 200)


# class SelectionBannerNewEventsSelectedCreateViewTest(TestBase):

#     def comprobation_event_selected(self):
#             self.post()
#             if not formset.cleaned_data[i]['selection']:
class EventTest(TestBase):

    def test_event_creation(self):
        w = EventFactory()
        self.assertTrue(isinstance(w, Event))
        event_list = Event.objects.all()
        event = event_list[len(event_list) - 1]
        self.assertEqual(event.title, w.title)


class EventViewTest(TestBase):

    def setUp(self):
        super(EventViewTest, self).setUp()
        from social_django.models import UserSocialAuth
        UserSocialAuth.objects.create(
            user=self.user,
            provider='eventbrite',
            extra_data={'access_token': 'user_token'},
        )

    @patch('banner.views.Eventbrite.get')
    def test_events_page_status_code(self, mock_eventbrite_get):
        response = self.client.get('/banner/new/')
        self.assertEqual(response.status_code, 200)

    @patch('banner.views.Eventbrite.get')
    def test_call_with_correct_parameters(self, mock_eventbrite_get):
        self.client.get('/banner/new/')
        self.assertEquals(
            mock_eventbrite_get.call_args_list[0][0][0],
            '/users/me/events/',
        )

    @skip('implementar pagina de error cuando no hay eventos en Eventbrite')
    @patch('banner.views.Eventbrite.get')
    def test_error_none_events(self, mock_eventbrite_get):
        response = self.client.get('/banner/new/')
        self.assertContains(response, 'You dont have any event in Eventbrite')

    @patch('banner.views.Eventbrite.get')
    def test_call_once_api(self, mock_eventbrite_get):
        self.client.get('/banner/new/')
        mock_eventbrite_get.assert_called_once()













# class TestSignup(unittest.TestCase):

#     def setUp(self):
#         self.driver = webdriver.Firefox()

#     def test_signup_fire(self):
#         self.driver.get("http://localhost:8000/add/")
#         self.driver.find_element_by_id('id_title').send_keys("test title")
#         self.driver.find_element_by_id('id_body').send_keys("test body")
#         self.driver.find_element_by_id('submit').click()
#         self.assertIn("http://localhost:8000/", self.driver.current_url)

#     def tearDown(self):
#         self.driver.quit

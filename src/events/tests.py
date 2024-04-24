from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from events.helpers import send_event_registration_email
from events.models import Event
from events.models import EventRegistration
from events.serializers import EventSerializer

__USER = {
    'username': 'Johny', 'email': 'johny@mail.ua', 'password': 'qwerty'
}

class CreateUser(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(**globals()['__USER'])


class CreateEvent(CreateUser):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            title='My event',
            description='1st event',
            date='2024-04-23',
            location='Kyiv',
            organizer=self.user
        )


class CreateToken(CreateUser):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)


class EventModelTest(CreateEvent):
    def test_create_event_success(self):
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(self.event.title, 'My event')
        self.assertEqual(self.event.description, '1st event')
        self.assertEqual(self.event.location, 'Kyiv')
        self.assertEqual(self.event.organizer, self.user)


class EventRegistrationModelTest(CreateEvent):
    def test_create_event_registration_success(self):
        registration = EventRegistration.objects.create(
            user=self.user, event=self.event
        )
        self.assertEqual(EventRegistration.objects.count(), 1)
        self.assertEqual(registration.user, self.user)
        self.assertEqual(registration.event, self.event)


class UserCreationTestCase(APITestCase):
    def test_create_user_success(self):
        resp = self.client.post(reverse('register'), globals()['__USER'])
        user = User.objects.all()
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        self.assertEqual(user.count(), 1)

        user = user.first()
        self.assertEqual(user.username, 'Johny')
        self.assertEqual(user.email, 'johny@mail.ua')

    def test_create_user_without_password_fail(self):
        resp = self.client.post(
            reverse('register'),
            {'username': 'Johny', 'email': 'testuser@example.com'}
        )
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_user_with_existing_username_fail(self):
        User.objects.create_user('Johny', 'johny@mail.ua', 'qwerty')
        resp = self.client.post(reverse('register'), globals()['__USER'])
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase, CreateUser):
    def setUp(self):
        super().setUp()

    def test_login_success(self):
        resp = self.client.post(
            reverse('login'), {'username': 'Johny', 'password': 'qwerty'}
        )
        self.assertEqual(resp.status_code, HTTP_200_OK)

    def test_login_fail(self):
        resp = self.client.post(
            reverse('login'), {'username': 'Johny', 'password': 'wrongpwd'}
        )
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)


class UserLogoutTestCase(APITestCase, CreateToken):
    def setUp(self):
        super().setUp()

    def test_logout_success(self):
        resp = self.client.post(reverse('logout'))
        self.assertEqual(resp.status_code, HTTP_200_OK)

    def test_logout_without_token_fail(self):
        self.client.credentials()
        resp = self.client.post(reverse('logout'))
        self.assertEqual(resp.status_code, HTTP_401_UNAUTHORIZED)


class EventSerializerTestCase(APITestCase, CreateEvent):
    def setUp(self):
        super().setUp()
        self.serializer = EventSerializer(instance=self.event)

    def test_contains_expected_fields_success(self):
        self.assertCountEqual(
            self.serializer.data.keys(),
            ['title', 'description', 'date', 'location', 'organizer']
        )

    def test_title_field(self):
        self.assertEqual(self.serializer.data['title'], self.event.title)

    def test_description_field(self):
        self.assertEqual(
            self.serializer.data['description'], self.event.description
        )

    def test_date_field(self):
        self.assertEqual(self.serializer.data['date'], '2024-04-23')

    def test_location_field(self):
        self.assertEqual(self.serializer.data['location'], self.event.location)

    def test_organizer_field(self):
        self.assertEqual(
            self.serializer.data['organizer'], self.event.organizer.id
        )


class EventViewSetTestCase(APITestCase, CreateEvent, CreateToken):
    def setUp(self):
        super().setUp()

    def test_get_all_events(self):
        resp = self.client.get(reverse('event-list'))
        self.assertEqual(resp.status_code, HTTP_200_OK)

    def test_get_single_event_success(self):
        response = self.client.get(
            reverse('event-detail', kwargs={'pk': self.event.pk})
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_create_event_success(self):
        resp = self.client.post(
            reverse('event-list'),
            {
                'title': 'New 2nd event',
                'description': 'Lorem ipsum',
                'date': '2024-01-01',
                'location': 'Kryvyi Rih',
                'organizer': self.user.id
            }
        )
        self.assertEqual(resp.status_code, HTTP_201_CREATED)

    def test_update_event_success(self):
        resp = self.client.put(
            reverse('event-detail', kwargs={'pk': self.event.pk}),
            {
                'title': 'Updated Event',
                'description': 'Lorem ipsum',
                'date': '2024-01-02',
                'location': 'Kyiv',
                'organizer': self.user.id
            }
        )
        self.assertEqual(resp.status_code, HTTP_200_OK)

    def test_delete_event_success(self):
        resp = self.client.delete(
            reverse('event-detail', kwargs={'pk': self.event.pk})
        )
        self.assertEqual(resp.status_code, HTTP_204_NO_CONTENT)


class EventRegistrationViewTest(CreateEvent, CreateToken):
    def setUp(self):
        super().setUp()

    def test_register_for_event_success(self):
        resp = self.client.post(
            reverse('register-event', kwargs={'event_id': self.event.id})
        )
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        self.assertEqual(EventRegistration.objects.count(), 1)
        event = EventRegistration.objects.first()
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.event, self.event)

    def test_register_for_event_fail(self):
        self.client.credentials()
        resp = self.client.post(
            reverse('register-event', kwargs={'event_id': self.event.id})
        )
        self.assertEqual(resp.status_code, HTTP_401_UNAUTHORIZED)


class EventSearchTests(CreateEvent, CreateToken):
    def setUp(self):
        super().setUp()
        self.event2 = Event.objects.create(
            title='Test Event 2',
            description='This is test event 2',
            date='2024-01-09',
            location='Rio',
            organizer=self.user
        )

    def test_search_events_success(self):
        resp = self.client.get(
            reverse('search-event'), {'query': 'My event'}
        )
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['title'], 'My event')


class EventRegistrationEmailTest(CreateEvent):
    def setUp(self):
        super().setUp()

    @patch('events.helpers.send_mail')
    def test_send_event_registration_email_success(self, mock_email):
        send_event_registration_email(self.user, self.event)
        mock_email.assert_called_once_with(
            'Event registration',
            "Hi Johny,\n\nYou've successfully registered on My event",
            'mail@example.com',
            ['johny@mail.ua']
        )

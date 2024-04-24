from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from events.models import Event
from events.models import EventRegistration


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'username', 'email', 'password'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = 'title', 'description', 'date', 'location', 'organizer'


class EventRegistrationSerializer(ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = 'user', 'event'
        read_only_fields = 'user', 'event'

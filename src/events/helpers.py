from django.core.mail import send_mail


def send_event_registration_email(user, event):
    send_mail(
        'Event registration',
        f"Hi {user.username},\n\nYou've successfully registered on {event.title}",
        'mail@example.com',
        [user.email]
    )

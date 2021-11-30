import datetime
from celery import Celery
from firebase_admin import messaging
celery = Celery('task', broker='amqp://guest@localhost//')

@celery.task
def send_notification(list_token, id, meg):
    registration_tokens = list_token

    message = messaging.MulticastMessage(
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='normal',
            notification=messaging.AndroidNotification(
                title=id,
                body=meg,
                icon='stock_ticker_update',
                color='#f45342'
            ),
        ),
        tokens=registration_tokens,
    )
    response = messaging.send_multicast(message)
    print('{0} messages were sent successfully'.format(response.success_count))
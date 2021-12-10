import datetime
import firebase_admin
from celery import Celery
from firebase_admin import messaging
from firebase_admin import credentials
celery = Celery('task', broker='amqp://guest@localhost//')
cred = credentials.Certificate("android-f8ca4-firebase-adminsdk-cc61u-29ef632831.json")
#app_options = {'projectId':'project-352564192482'}
firebase_admin.initialize_app(cred)
@celery.task
def send_notification(list_token, id, chatroom_name, meg):
    registration_tokens = list_token
    print(registration_tokens)
    print('=====123======')
    print(id)
    print(chatroom_name)

    message = messaging.MulticastMessage(
        #android=messaging.AndroidConfig(
        #    ttl=datetime.timedelta(seconds=3600),
        #    priority='normal',
            #notification=messaging.AndroidNotification(
            #    title=chatroom_name,
            #    body=meg,
            #    icon='stock_ticker_update',
            #    color='#f45342'
            #),
        #),
        data={'id':str(id),'chatroom_name':chatroom_name, 'meg':meg},
        tokens=registration_tokens,
    )
    print('testtttttttttttttttttttttttttt')
    try:
        response = messaging.send_multicast(message)
        print('{0} messages were sent successfully'.format(response.success_count))
    except:
        print('errorrrrrrrrrrrrrrrrrrrrrrrrr')
   # message = messaging.MulticastMessage(
        #notification=messaging.Notification(
         #   title=id,
        #    body=meg
       # ),
      #  data=None,
     #   tokens=registration_tokens,
    #)
    response = messaging.send_multicast(message)
    print('{0} messages were sent successfully'.format(response.success_count))

# from twilio.rest import Client 
import os 
import requests
from .config import Settings

settings = Settings()

# from twilio.base.exceptions import TwilioRestException

# load_dotenv()  

# account_sid = os.getenv("ACCOUNT_SID")
# auth_token = os.getenv("AUTH_TOKEN")

# client = Client(account_sid, auth_token)

# def send_sms_service(sender, receiver, message_body):
#     try:
#         twilio_message = client.messages.create(
#             from_=sender,
#             to=receiver,
#             body=message_body
#         )
#         return twilio_message  
#     except TwilioRestException as e:
#         print(f"Twilio error: {e}")
#         return None
#     except Exception as e:
#         print(f"General error: {e}")
#         return None




endPoint = 'https://api.mnotify.com/api/sms/quick'

apiKey = settings.api_key

def send_sms_service(receiver,message):
    try:
        data = {
        'recipient[]': [receiver],
        'sender': 'EricaNotify',
        'message': message,
        'is_schedule': False,
        'schedule_date': ''
        }
        url = endPoint + '?key=' + apiKey
        response = requests.post(url, data)
        data = response.json()

        return data
    except Exception as e:
        print(f"Failed to send sms to external gateway: {e}")
        return None
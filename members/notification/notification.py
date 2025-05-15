import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("google-services.json")
firebase_admin.initialize_app(cred)

def send_notification_to_token(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    response = messaging.send(message)
    return response

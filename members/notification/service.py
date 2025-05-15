# notifications/services.py
import os
import firebase_admin
from firebase_admin import credentials, messaging
from members.models import Member  # ajuste ce chemin à ta structure réelle
from yourapp.models import DeviceToken  # remplace `yourapp` par le vrai nom

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cred_path = os.path.join(BASE_DIR, "firebase-adminsdk.json")

# Initialisation Firebase une seule fois
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def send_notification_to_token(token, title, body):
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
        )
        response = messaging.send(message)
        print(f"Envoyé à {token[:10]}...: {response}")
    except Exception as e:
        print(f"Erreur avec {token[:10]}...: {e}")

def notify_non_contributors():
    members = Member.objects.filter(has_contribued_for_session=False)

    for member in members:
        device_tokens = DeviceToken.objects.filter(user=member.user_id)
        for token in device_tokens:
            send_notification_to_token(
                token.token,
                title="Contribution manquante",
                body=f"Bonjour {member.username}, vous n'avez pas encore contribué à la session."
            )

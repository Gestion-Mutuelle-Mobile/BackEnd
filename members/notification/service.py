# notifications/services.py
import os
import firebase_admin
from firebase_admin import credentials, messaging
from members.models import User, Member, Administrator, Notification # ajuste ce chemin à ta structure réelle
from members.models import DeviceToken  # remplace `yourapp` par le vrai nom

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # ← ne pas aller trop haut
cred_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'google-services.json'))

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
    print("membres sont :", members)

    for member in members:
        device_tokens = DeviceToken.objects.filter(user=member.user_id)
        for token in device_tokens:
            title = "Contribution manquante"
            body = f"Salut {member.username}, vous n'avez pas encore payé votre contribution de la session."

            print("le token est :", token.token)
            send_notification_to_token(token.token, title=title, body=body)

            # Enregistrement de la notification
            Notification.objects.create(
                user=token.user,
                title=title,
                body=body
            )

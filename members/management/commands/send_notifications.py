from django.core.management.base import BaseCommand
from members.notification.service import notify_non_contributors

class Command(BaseCommand):
    help = "Envoie des notifications aux membres non en règle"

    def handle(self, *args, **options):
        notify_non_contributors()
        self.stdout.write(self.style.SUCCESS('Notifications envoyées avec succès.'))

# mutualApp/signals.py

from django.db.models.signals import post_delete
from django.dispatch import receiver
from operationApp.models import ObligatoryContribution, FondSocial

@receiver(post_delete, sender=ObligatoryContribution)
def update_fond_social_on_delete(sender, instance, **kwargs):
    # Obtenir la session associée à la contribution supprimée
    session = instance.session_id
    if session:
        # Rechercher ou créer le fonds social pour cette session
        fond_social, created = FondSocial.objects.get_or_create(session=session)

        # Déduire le montant de la contribution supprimée
        fond_social.amount -= instance.amount
        fond_social.save()

        # Mettre à jour le fonds social en appelant sa méthode update_fonds_social
        fond_social.update_fonds_social()

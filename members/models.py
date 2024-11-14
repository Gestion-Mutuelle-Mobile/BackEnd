from django.db import models
from users.models import User
from administrators.models import Administrator
from decimal import Decimal
from datetime import timedelta
# Create your models here.
class Member(models.Model):
    # id = models.IntegerField(max_length=10)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    username = models.CharField(max_length=8,  blank=True)

    active = models.BooleanField(default=True)
    social_crown = models.IntegerField(default=0)
    inscription = models.IntegerField(default=10000)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Appeler le save parent pour enregistrer le membre
        super().save(*args, **kwargs)

        # Rechercher la session active la plus récente
        from mutualApp.models import Session
        session = Session.objects.filter(active=True).order_by('-create_at').first()

        if session:
            # Vérifier si un fonds social existe pour cette session
            from mutualApp.models import FondSocial
            fond_social, created = FondSocial.objects.get_or_create(session=session)

            # Si le fonds social existe déjà, on le met à jour ; sinon, il est créé avec l'inscription du membre
            if not created:
                fond_social.update_fonds_social()
            else:
                # Initialiser le montant du fonds social avec l'inscription du membre
                fond_social.update_fonds_social()
    def calculate_debt(self):
        """
        Calcule le montant total restant à rembourser par le membre.
        Somme de (amount_to_pay - amount_paid) pour tous les emprunts actifs.
        """
        total_debt = self.borrowing_set.filter(state=True).aggregate(
            debt=models.Sum(models.F('amount_to_pay') - models.F('amount_paid'))
        )['debt'] or 0
        return total_debt

    def has_open_help(self):
        """
        Vérifie si une aide est ouverte pour le membre (state=1).
        """
        return self.help_set.filter(state=1).exists()

    def calculate_total_savings(self):
        """
        Calcule l'épargne totale du membre dans la session active la plus récente.
        """
        from mutualApp.models import Session
        session = Session.objects.filter(active=True).order_by('-create_at').first()
        if session:
            from operationApp.models import Epargne
            return Epargne.objects.filter(member_id=self, session=session).aggregate(
                total_savings=models.Sum('amount')
            )['total_savings'] or 0
        return 0

    def calculate_tresorerie_percentage(self):
        """
        Calcule le pourcentage de la treso que représente l'épargne totale
        du membre pour la session active la plus récente.
        """
        from mutualApp.models import Session
        from operationApp.models import Tresorerie

        session = Session.objects.filter(active=True).order_by('-create_at').first()
        if not session:
            return Decimal(0)

        total_savings = self.calculate_total_savings()
        tresorerie = Tresorerie.objects.filter(session=session).first()

        if tresorerie and tresorerie.amount > 0:
            return (Decimal(total_savings) / tresorerie.amount) * 100
        return Decimal(0)

    def __str__(self):
        return f"MEMBRE : {self.username} (ID: {self.user_id})"


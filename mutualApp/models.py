

from django.db import models
from django.utils import timezone
from datetime import timedelta

from members.models import Member


# Create your models here.



# Create your models here.
class Exercise(models.Model):
    active = models.BooleanField(default=True)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL,null=True)
    create_at = models.DateTimeField(auto_now=True)
    def update_active(self):
        """
        Met à jour le champ 'active' à False si l'exercice a été créé il y a plus d'un an.
        """
        one_year_ago = timezone.now() - timedelta(days=365)
        if self.create_at < one_year_ago:
            self.active = False
            self.save()
    def getYear(self):
        return self.create_at.year
    def __str__(self):
        return str(f"Exercice {self.id} de {self.create_at}")

class Session(models.Model):
    exercise_id = models.ForeignKey('mutualApp.Exercise', on_delete=models.CASCADE)
    state = models.CharField(max_length=255, default='SAVING')
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL,null=True)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Avant de sauvegarder une nouvelle session, désactive la session active existante,
        s'il y en a une, pour garantir qu'il n'y ait qu'une seule session active.
        """
        if self.active:
            # Désactive toute autre session active
            Session.objects.filter(active=True).update(active=False)

        # Sauvegarde la nouvelle session
        super().save(*args, **kwargs)
    def update_active(self):
        """
        Met à jour le champ 'active' à False si la session a été créé il y a plus d'un mois.
        """
        one_month_ago = timezone.now() - timedelta(days=30)
        if self.create_at < one_month_ago:
            self.active = False
            self.save()

    def __str__(self):
        return str(f"Session de {self.create_at}")






# Modèle FondSocial
class FondSocial(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def update_fonds_social(self):
        from operationApp.models import ObligatoryContribution

        """
        Met à jour le fond social en ajoutant les montants des contributions
        obligatoires créées après la dernière mise à jour, ainsi que les frais
        d'inscription des membres actifs.
        """
        # Contributions obligatoires depuis la dernière mise à jour
        self.updated_at = timezone.now()
        new_contributions = ObligatoryContribution.objects.filter(
            session=self.session,
            create_at__gt=self.updated_at,
            member__active=True  # seulement les membres actifs
        ).aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0

        # Frais d'inscription des nouveaux membres actifs depuis la dernière mise à jour
        new_inscriptions = Member.objects.filter(
            active=1,
            # contribution__session=self.session,  # contributions dans la session en cours
            create_at__gt=self.updated_at
        ).aggregate(total_inscription=models.Sum('inscription'))['total_inscription'] or 0

        # Mise à jour du montant du fond social
        self.amount += new_contributions + new_inscriptions
        self.save()
    def substract(self,amount):
        self.amount -= amount
        self.updated_at = timezone.now()
        self.save()
    def addAmmount(self,amount):
        self.amount += amount
        self.updated_at = timezone.now()
        self.save()
    def __str__(self):
        return f"Fonds social de la Session {self.session.create_at} montant : {self.amount}"


# Modèle Tresorerie (structure de base)
class Tresorerie(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    # Placeholder pour la méthode update_treso, à implémenter plus tard.
    def update_treso(self):
        self.updated_at = timezone.now()
        pass

    def substract(self,amount):
        self.amount -= amount
        self.updated_at = timezone.now()
        self.save()
    def addAmmount(self,amount):
        self.amount += amount
        self.updated_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Trésorerie de la Session {self.session.create_at} montant : {self.amount}"





import decimal
from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime


# Create your models here.



# Create your models here.
class Exercise(models.Model):
    active = models.BooleanField(default=True)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL, null=True)
    create_at = models.DateTimeField(auto_now_add=True,editable=True)
    end_date = models.DateTimeField(null=True, blank=True,editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:  # Nouvel exercice
            # Désactive les autres exercices
            Exercise.objects.filter(active=True).update(active=False)
            # Définit la date de fin à un an
            self.end_date = timezone.now() + timedelta(days=365)
        super().save(*args, **kwargs)

    def close_exercise(self):
        """Ferme l'exercice et transfère les fonds vers un nouvel exercice"""
        if self.active:
            self.active = False
            self.end_date = timezone.now()
            self.save()

            # Crée un nouvel exercice
            new_exercise = Exercise.objects.create(
                administrator_id=self.administrator_id,
                active=True
            )

            # Transfère le fond social
            old_fond = FondSocial.objects.get(exercise=self)
            FondSocial.objects.create(
                exercise=new_exercise,
                amount=old_fond.amount
            )

            # Transfère la trésorerie
            old_treso = Tresorerie.objects.get(exercise=self)
            Tresorerie.objects.create(
                exercise=new_exercise,
                amount=old_treso.amount
            )

    def __str__(self):
        return f"Exercice {self.id} ({self.create_at.year})"

class Session(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True,editable=False)
    state = models.CharField(max_length=20, choices=[
        ('SAVING', 'Épargne'),
        ('BORROWING', 'Emprunt'),
        ('CLOSED', 'Fermée')
    ], default='SAVING')

    def save(self, *args, **kwargs):
        from members.models import Member
        if not self.pk:  # Nouvelle session
            # Désactive les autres sessions de l'exercice
            Session.objects.filter(
                exercise=self.exercise,
                active=True
            ).update(active=False)
            # Définit la date de fin à un mois
            self.end_date = timezone.now() + timedelta(days=30)
        members = Member.objects.all()
        if members :
            for member in members:
                member.update_contrib_status(status=False)
        super().save(*args, **kwargs)

    def close_session(self):
        """Ferme la session actuelle"""
        self.active = False
        self.state = 'CLOSED'
        self.end_date = timezone.now()
        self.save()

    def __str__(self):
        return f"Session du {self.create_at.strftime('%d/%m/%Y')} - {self.state}"






# Modèle FondSocial
class FondSocial(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def add_amount(self, amount):
        """Ajoute un montant au fond social"""
        self.amount += decimal.Decimal(amount) 
        self.save()

    def subtract_amount(self, amount):
        """Soustrait un montant du fond social"""
        if self.amount >= amount:
            self.amount -= amount
            self.save()
        else:
            raise ValueError("Fonds insuffisants dans le fond social")

    def __str__(self):
        return f"Fond social de l'exercice {self.exercise.create_at.year}: {self.amount}"





class Tresorerie(models.Model):
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def add_amount(self, amount):
        """Ajoute un montant à la trésorerie"""
        self.amount += amount
        self.save()

    def subtract_amount(self, amount):
        """Soustrait un montant de la trésorerie"""
        if self.amount >= amount:
            self.amount -= amount
            self.save()
        else:
            raise ValueError("Fonds insuffisants dans la trésorerie")

    def get_total_savings(self):
        from operationApp.models import Epargne

        """Calcule le total des épargnes pour l'exercice"""
        return Epargne.objects.filter(exercise_id=self.exercise).aggregate(
            total=models.Sum('amount'))['total'] or 0

    def get_total_interest(self):
        from operationApp.models import Epargne

        """Calcule le total des intérêts pour l'exercice"""
        return Epargne.objects.filter(exercise_id=self.exercise).aggregate(
            total=models.Sum('interest'))['total'] or 0
# Classe de log pour suivre les transactions
class TransactionLog(models.Model):
    tresorerie = models.ForeignKey(Tresorerie, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
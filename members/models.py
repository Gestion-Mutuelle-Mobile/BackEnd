from django.db import models

from mutualApp.models import Exercise
from users.models import User
from administrators.models import Administrator
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone




class Member(models.Model):
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.CASCADE)
    username = models.CharField(max_length=8, blank=True)
    active = models.BooleanField(default=True)
    inscription = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    total_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_borrowings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_interest = models.FloatField( default=0)
    has_contribued_for_session=models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        from mutualApp.models import FondSocial, Exercise
        
        if not self.pk:  # Nouveau membre
            # Ajout des frais d'inscription au fond social
            exercise = Exercise.objects.filter(active=True).first()
        
            if exercise:
                fond_social, _ = FondSocial.objects.get_or_create(exercise=exercise)
                fond_social.add_amount(self.inscription)
        super().save(*args, **kwargs)
    def update_contrib_status(self,status=True):
        if status==False:
            self.has_contribued_for_session=status
        else:
            self.has_contribued_for_session=(not self.has_contribued_for_session)
        self.save()

    def get_current_savings(self):
        from operationApp.models import Epargne
        """Calcule l'épargne totale dans l'exercice actif"""
        exercise = Exercise.objects.filter(active=True).first()
        if exercise:
            self.total_savings = Epargne.objects.filter(
                member_id=self,
                exercise_id=exercise
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            return self.total_savings
        return 0
    def calculate_total_savings(self):
        from operationApp.models import Epargne
        """Calcule l'épargne totale dans l'exercice actif"""
        exercise = Exercise.objects.filter(active=True).first()
        if exercise:
            self.total_savings = Epargne.objects.filter(
                member_id=self,
                exercise_id=exercise
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            return self.total_savings
        return 0

    def get_current_interest(self):
        from operationApp.models import Epargne

        """Calcule les intérêts totaux dans l'exercice actif"""
        exercise = Exercise.objects.filter(active=True).first()
        if exercise:
            self.total_interest = Epargne.objects.filter(
                member_id=self,
                exercise_id=exercise
            ).aggregate(total=models.Sum('interest'))['total'] or 0
            return self.total_interest

        return 0

    def get_active_borrowings(self):
        from operationApp.models import Borrowing

        """Retourne les emprunts actifs du membre"""
        return Borrowing.objects.filter(
            member_id=self,
            state=False
        )

    def get_total_debt(self):
        """Calcule la dette totale active"""
        borrowings = self.get_active_borrowings()
        self.total_borrowings = sum(b.amount_to_pay - b.amount_paid for b in borrowings)
        return self.total_borrowings
    def calculate_tresorerie_percentage(self):
        from mutualApp.models import Tresorerie
        treso= Tresorerie.objects.first()
        if treso and treso.amount !=0 :
            t=treso.amount
            return float(self.calculate_total_savings())*100/float(t) 
        
        else :
            return 0
    
    def calculate_debt(self):
        """Calcule la dette totale active"""
        borrowings = self.get_active_borrowings()
        self.total_borrowings = sum(b.amount_to_pay - b.amount_paid for b in borrowings)
        return self.total_borrowings

    def __str__(self):
        return f"MEMBRE : {self.username}"


# Create your models here.


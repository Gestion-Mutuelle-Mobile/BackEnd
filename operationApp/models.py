from django.db import models
from members.models import Member
from administrators.models import Administrator
from django.db import models
from django.utils import timezone
from mutualApp.models import Session, Tresorerie, FondSocial
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import models, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils.timezone import now


class Operation(models.Model):
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL, null=True,related_name='operations_from_operationApp')
    create_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE)
    exercise_id = models.ForeignKey('mutualApp.Exercise', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        """
        Reedéfinit la méthode save pour attribuer automatiquement la dernière session active.
        Si aucune session active n'est trouvée, l'opération n'est pas sauvegardée.
        """
        from mutualApp.models import Session

        # Recherche la dernière session active
        active_session = Session.objects.filter(active=True).order_by('-create_at').first()

        if active_session:
            self.session_id = active_session  # Assigne la session active
            self.exercise_id = active_session.exercise  # Assigne l'exercice de la session
            super().save(*args, **kwargs)    # Appelle la méthode save parente
        else:
            # Message si aucune session active n'est trouvée
            print("Aucune session active pour le moment. L'opération ne peut pas être enregistrée.")


# Create your models here.
class Contribution(models.Model):
    id=models.IntegerField(auto_created=True, primary_key=True,editable=False)
    member_id = models.ForeignKey('members.Member', on_delete=models.SET_NULL,null=True,blank=True,related_name='contributions_from_operationApp')
    state = models.BooleanField(default=True)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL, null=True)
    create_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE)
    exercise_id = models.ForeignKey('mutualApp.Exercise', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        """
        Reedéfinit la méthode save pour attribuer automatiquement la dernière session active.
        Si aucune session active n'est trouvée, l'opération n'est pas sauvegardée.
        """
        from mutualApp.models import Session

        # Recherche la dernière session active
        active_session = Session.objects.filter(active=True).order_by('-create_at').first()

        if active_session:
            self.session_id = active_session  # Assigne la session active
            self.exercise_id = active_session.exercise_id  # Assigne l'exercice de la session

            super().save(*args, **kwargs)    # Appelle la méthode save parente
        else:
            # Message si aucune session active n'est trouvée
            print("Aucune session active pour le moment. L'opération ne peut pas être enregistrée.")

class PersonalContribution(Contribution):
    date = models.DateTimeField(auto_now=True)
    help_id = models.ForeignKey('operationApp.Help', on_delete=models.SET_NULL,null=True) #l'aide en question
    amount = models.IntegerField(default=0)
    
class Help(Operation):
    help_type_id = models.ForeignKey('operationApp.HelpType', on_delete=models.CASCADE)
    amount_expected = models.FloatField(blank=True, null=True)
    comments = models.TextField(max_length=255)
    state = models.BooleanField(default=True)
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE,related_name='operation_help_set') # le memebre qui a besoin de l'aide
    collected_amount = models.FloatField(default=0)
    def __str__(self):
        return f"Aide au membre {self.member_id.username}"
    def save(self, *args, **kwargs):
        self.amount_expected=self.help_type_id.amount
        super().save(*args, **kwargs)    # Appelle la méthode save parente
    def calculate_help_amount(self):
        from django.db.models import Sum

        """
        Calcule le montant total collecté pour cette aide à partir des contributions personnelles.
        """
        self.collected_amount = PersonalContribution.objects.filter(
            help_id=self,
            state=True  # Seules les contributions actives
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        return self.collected_amount


class HelpType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255 , null=True ,blank=True,default='type d\'aide')
    amount = models.FloatField(default=0)

    def __str__(self):
        return self.name


class ObligatoryContribution(Contribution):
    contributed = models.BooleanField(default=False)
    amount = models.FloatField(default=10000)
    def save(self, *args, **kwargs):
        fonds_social=FondSocial.objects.get(exercise=self.exercise_id)
        fonds_social.add_amount(self.amount)
        self.member_id.update_contrib_status()

        super().save(*args, **kwargs)    # Appelle la méthode
    def __str__(self):
        return f"Contribution Obligatoire de {self.member_id.username}"


# model du pret

from django.db import models, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal


class Borrowing(Operation):
    amount_borrowed = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date_line = models.DateTimeField()
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE,related_name='borrowings_from_operationApp')
    state = models.BooleanField(default=False)
    late = models.BooleanField(default=False)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=3.00)  # Taux fixé à 3%
    interest_distribution = models.JSONField(default=dict)  # Stockage de la distribution des intérêts

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.check_and_update_late_status()

        if not self.pk:  # Nouveau prêt
            # Calcul du montant des intérêts (3% du montant emprunté)
            interest_amount = (self.amount_borrowed * self.interest_rate) / 100
            self.amount_to_pay = self.amount_borrowed + interest_amount

            if not self.payment_date_line:
                self.payment_date_line = timezone.now() + timedelta(days=30)

            # Distribution des intérêts aux membres
            self.distribute_interest(interest_amount)

            # Mise à jour de la trésorerie
            tresorerie = Tresorerie.objects.get(exercise=self.exercise_id)
            tresorerie.substract(self.amount_borrowed)
            tresorerie.save()

        super().save(*args, **kwargs)

    def distribute_interest(self, total_interest):
        """Distribue les intérêts aux membres proportionnellement à leurs épargnes"""
        from operationApp.models import Epargne

        # Récupération de toutes les épargnes de l'exercice en cours
        epargnes = Epargne.objects.filter(exercise_id=self.exercise_id)
        total_savings = sum(epargne.amount for epargne in epargnes)

        # Distribution des intérêts
        distribution = {}
        for epargne in epargnes:
            if total_savings > 0:
                # Calcul de l'intérêt proportionnel pour cette épargne
                interest_share = (epargne.amount / total_savings) * total_interest

                # Mise à jour de l'intérêt de l'épargne
                epargne.interest += float(interest_share)
                epargne.save()

                # Mise à jour de l'intérêt total du membre
                member = epargne.member_id
                member.total_interest += float(interest_share)
                member.save()

                # Enregistrement dans la distribution
                distribution[str(epargne.member_id.id)] = float(interest_share)

        self.interest_distribution = distribution

    def check_and_update_late_status(self):
        """
        Vérifie si la date limite de paiement est passée et met à jour l'état `state`.
        """
        if now() > self.payment_date_line and not self.state:
            self.late = True  # Mettre à jour le statut à "en retard"
            self.save()  # Sauvegarder la mise à jour


# model de l'epargne
class Epargne(Operation):
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE,related_name='epargnes_from_operationApp')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Intérêts accumulés

    def save(self, *args, **kwargs):
        if not self.pk:  # Nouvelle épargne
            super().save(*args, **kwargs)

            # Mise à jour de la trésorerie
            tresorerie = Tresorerie.objects.get(exercise=self.exercise_id)
            tresorerie.add_amount(self.amount)
            tresorerie.save()

    def get_total_amount(self):
        """Retourne le montant total incluant les intérêts"""
        return self.amount + self.interest



# model du remboursement
class Refund(models.Model):
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE,related_name='refunds_from_operationApp')
    borrowing_id = models.ForeignKey('Borrowing', on_delete=models.CASCADE)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL, null=True)
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE)
    exercise_id = models.ForeignKey('mutualApp.Exercise', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.pk:  # Nouveau remboursement
            borrowing = self.borrowing_id
            borrowing.check_and_update_late_status()

            # Mise à jour du montant remboursé de l'emprunt
            borrowing.amount_paid += self.amount
            if borrowing.amount_paid >= borrowing.amount_to_pay:
                borrowing.state = True  # Emprunt entièrement remboursé
            borrowing.save()

            # Mise à jour de la trésorerie
            tresorerie = Tresorerie.objects.get(exercise=self.exercise_id)
            tresorerie.add_amount(self.amount)
            tresorerie.save()

        super().save(*args, **kwargs)
# Nouvelle classe de trace pour les redistributions
class RefundDistributionTrace(models.Model):
    epargne = models.ForeignKey(Epargne, on_delete=models.CASCADE)
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE)
    benefit_share = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    real_time_amount_before = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    real_time_amount_after = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
class LoanUtilizationTrace(models.Model):
    epargne = models.ForeignKey(Epargne, on_delete=models.CASCADE)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    amount_used = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    real_time_amount_before = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    real_time_amount_after = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
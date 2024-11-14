from django.db import models
from members.models import Member
from administrators.models import Administrator
from django.db import models
from django.utils import timezone
from mutualApp.models import Session, Tresorerie, FondSocial
from decimal import Decimal
from datetime import timedelta

class Operation(models.Model):
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL,null=True)
    create_at = models.DateTimeField(auto_now=True)
    session_id= models.ForeignKey('mutualApp.Session',on_delete=models.CASCADE)

# Create your models here.
class Contribution(Operation):
    member_id = models.ForeignKey('members.Member', on_delete=models.SET_NULL,null=True)
    state = models.BooleanField(default=True)

class PersonalContribution(Contribution):
    date = models.CharField(max_length=20)
    help_id = models.ForeignKey('operationApp.Help', on_delete=models.SET_NULL,null=True) #l'aide en question
    amount = models.IntegerField(default=0)
    def __str__(self):
        return f"Contribution Personnelle de {self.member_id.username} pour l'aide a {self.help_id.member_id.username}"

class Help(Operation):
    limit_date = models.DateField()
    amount_expected = models.IntegerField()
    comments = models.TextField(max_length=255)
    state = models.BooleanField(default=True)
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE,related_name='operation_help_set') # le memebre qui a besoin de l'aide

    def __str__(self):
        return f"Aide au membre {self.member_id.username}"
    def calculate_help_amount(self):
        from django.db.models import Sum

        """
        Calcule le montant total collecté pour cette aide à partir des contributions personnelles.
        """
        collected_amount = PersonalContribution.objects.filter(
            help_id=self,
            state=True  # Seules les contributions actives
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        return collected_amount

class ObligatoryContribution(Operation):
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE)
    contributed = models.BooleanField(default=False)
    amount = models.IntegerField(default=10000)
    def __str__(self):
        return f"Contribution Obligatoire de {self.member_id.username}"

    def save(self, *args, **kwargs):
        """
        Lors de l'enregistrement d'une contribution obligatoire, met à jour le fond social
        de la session correspondante.
        """
        super().save(*args, **kwargs)

        # Mettre à jour le FondSocial de la session
        session = self.session_id  # session liée à l'opération
        from mutualApp.models import FondSocial
        fond_social = FondSocial.objects.filter(session=session).first()
        if fond_social:
            fond_social.update_fonds_social()

# model du pret
class Borrowing(Operation):
    interest = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_borrowed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_date_line = models.DateTimeField(blank=True, null=True)
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='borrowings_from_operation')
    state = models.BooleanField(default=False)  # False = non remboursé, True = remboursé

    def save(self, *args, **kwargs):
        # Calculer l'intérêt comme 5% du montant emprunté
        if self.amount_borrowed is not None:
            self.interest = self.amount_borrowed * 0.05

            # Calculer le montant total à rembourser (emprunté + intérêts)
            self.amount_to_pay = self.amount_borrowed + self.interest

            # Calculer la date limite de paiement (30 jours après la date de création)
            if not self.payment_date_line:
                self.payment_date_line = timezone.now() + timedelta(days=30)

        # Appeler la méthode save parent pour enregistrer les modifications
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Prêt de {self.amount_borrowed} pour {self.member_id.username}, à rembourser avant le {self.payment_date_line}"

# model de l'epargne
class Epargne(Operation):
    # id = models.IntegerField(max_length=10)
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='epargne_from_operation')
    amount = models.IntegerField()

    def save(self, *args, **kwargs):
        # Enregistrer l'épargne
        super().save(*args, **kwargs)

        # Mise à jour de la trésorerie de la session
        session = self.session_id  # session liée à l'opération
        tresorerie = Tresorerie.objects.filter(session=session).first()
        if tresorerie:
            tresorerie.amount += Decimal(self.amount)
            tresorerie.update_treso()

    def calculate_tresorerie_percentage(self):
        """
        Calcule le pourcentage de la treso que représente cette épargne
        pour la session associée.
        """
        session = self.session_id
        tresorerie = Tresorerie.objects.filter(session=session).first()
        if tresorerie and tresorerie.amount > 0:
            return (Decimal(self.amount) / tresorerie.amount) * 100
        return Decimal(0)

# model du remboursement
class Refund(models.Model):
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.CASCADE,
                                         related_name='refunds_from_operation')
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE, default=1,
                                  related_name='refunds_from_operation')
    borrowing_id = models.ForeignKey('operationApp.Borrowing', on_delete=models.CASCADE, null=True,
                                     related_name='refunds_from_operation')
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE, related_name='refunds_from_operation')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Appeler le save parent pour enregistrer le remboursement
        super().save(*args, **kwargs)

        # Mettre à jour l'emprunt avec le montant remboursé
        borrowing = self.borrowing_id
        borrowing.amount_paid += self.amount
        borrowing.save()

        # Vérifier si le membre a des épargnes dans la même session que le prêt
        session = borrowing.session_id
        total_savings = self.member_id.calculate_total_savings()
        tresorerie = Tresorerie.objects.filter(session=session).first()

        # Assurez-vous que la trésorerie et l'épargne totale existent pour calculer la part de remboursement
        if total_savings > 0 and tresorerie and tresorerie.amount > 0:
            # Calculer le pourcentage de remboursement à distribuer à chaque épargne
            percentage = Decimal(total_savings) / tresorerie.amount
            refund_share = self.amount * percentage

            # Obtenir toutes les épargnes du membre dans cette session
            savings = Epargne.objects.filter(member_id=self.member_id, session=session)

            # Calculer la part de chaque épargne en fonction de sa proportion
            for saving in savings:
                saving_percentage = Decimal(saving.amount) / total_savings
                amount_to_add = refund_share * saving_percentage
                saving.amount += amount_to_add
                saving.save()

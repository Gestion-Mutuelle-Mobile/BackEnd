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

class Operation(models.Model):
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL, null=True)
    create_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE)

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
            super().save(*args, **kwargs)    # Appelle la méthode save parente
        else:
            # Message si aucune session active n'est trouvée
            print("Aucune session active pour le moment. L'opération ne peut pas être enregistrée.")


# Create your models here.
class Contribution(models.Model):
    id=models.IntegerField(auto_created=True, primary_key=True,editable=False)
    member_id = models.ForeignKey('members.Member', on_delete=models.SET_NULL,null=True,blank=True)
    state = models.BooleanField(default=True)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL, null=True)
    create_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE)
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
            super().save(*args, **kwargs)    # Appelle la méthode save parente
        else:
            # Message si aucune session active n'est trouvée
            print("Aucune session active pour le moment. L'opération ne peut pas être enregistrée.")

class PersonalContribution(Contribution):
    date = models.DateTimeField(auto_now=True)
    help_id = models.ForeignKey('operationApp.Help', on_delete=models.SET_NULL,null=True) #l'aide en question
    amount = models.IntegerField(default=0)
    
class Help(Operation):
    limit_date = models.DateField()
    amount_expected = models.FloatField()
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

class ObligatoryContribution(Contribution):
    contributed = models.BooleanField(default=False)
    amount = models.FloatField(default=10000)

    def __str__(self):
        return f"Contribution Obligatoire de {self.member_id.username}"


# model du pret

from django.db import models, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal

class Borrowing(Operation):
    interest = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_borrowed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_date_line = models.DateTimeField(blank=True, null=True)
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='borrowings_from_operation')
    state = models.BooleanField(default=False)
    loan_distribution = models.JSONField(default=dict, blank=True, null=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.amount_borrowed is not None and not self.pk:  # Seulement pour les nouveaux emprunts
            self.interest = Decimal(float(self.amount_borrowed) * 0.05)
            self.amount_to_pay = self.amount_borrowed + self.interest
            
            if not self.payment_date_line:
                self.payment_date_line = timezone.now() + timedelta(days=30)
            
            super().save(*args, **kwargs)  # Sauvegarde initiale avant distribution
            self.distribute_loan()
        else:
            super().save(*args, **kwargs)

    def distribute_loan(self):
        from members.models import Member
        active_members = Member.objects.filter(active=True)
        total_members = active_members.count()
        
        if total_members == 0:
            raise ValidationError("Aucun membre actif pour répartir le prêt")
        
        amount_per_member = self.amount_borrowed / total_members
        self.loan_distribution = {}
        remaining_amount = self.amount_borrowed
        
        for member in active_members:
            member_savings = member.calculate_total_savings()
            
            if member_savings > 0:
                contribution = min(member_savings, amount_per_member)
                self.update_member_savings(member, contribution)
                self.loan_distribution[str(member.id)] = float(contribution)
                remaining_amount -= contribution
        
        if remaining_amount > 0:
            self.handle_remaining_loan(remaining_amount)

    def update_member_savings(self, member, amount):
        from operationApp.models import Epargne
        savings = Epargne.objects.filter(
            member_id=member, 
            session_id=self.session_id
        ).first()
        
        if savings:
            old_amount = savings.real_time_amount
            savings.real_time_amount -= amount
            savings.save()
            
            LoanUtilizationTrace.objects.create(
                epargne=savings,
                borrowing=self,
                amount_used=amount,
                real_time_amount_before=old_amount,
                real_time_amount_after=savings.real_time_amount
            )
    def handle_remaining_loan(self, remaining_amount):
        # Logique de gestion du montant résiduel
        # On le répartit entre les membres ayant encore de l'épargne
        from members.models import Member
        
        active_members = Member.objects.filter(active=True)
        eligible_members = [
            m for m in active_members 
            if m.calculate_total_savings() > 0
        ]
        
        if not eligible_members:
            raise ValidationError("Aucun membre n'a suffisamment d'épargne")
        
        amount_per_remaining_member = remaining_amount / len(eligible_members)
        
        for member in eligible_members:
            # Mise à jour de l'épargne et de la distribution
            self.update_member_savings(member, amount_per_remaining_member)
            
            current_contribution = self.loan_distribution.get(str(member.id), 0)
            self.loan_distribution[str(member.id)] = current_contribution + float(amount_per_remaining_member)



# model de l'epargne
class Epargne(Operation):
    # Champs existants conservés
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='epargne_from_operation')
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)  # #modification: passage en DecimalField
    
    # #modification: Ajout de champs pour suivre l'épargne de base et en temps réel
    base_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    real_time_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    
    def save(self, *args, **kwargs):
        # Initialisation des montants si c'est une nouvelle épargne
        if not self.pk:
            self.base_amount = self.amount
            self.real_time_amount = self.amount
        
        # Sauvegarde de l'épargne
        super().save(*args, **kwargs)
        
        # Mise à jour de la trésorerie
        session = self.session_id
        if session:
            tresorerie, created = Tresorerie.objects.get_or_create(
                session=session, 
                defaults={'amount': Decimal(self.amount)}
            )
            
            if not created:
                tresorerie.amount += Decimal(self.amount)
                tresorerie.update_treso()
    
    def update_real_time_amount(self, amount_to_subtract):
        """
        Méthode pour mettre à jour le montant en temps réel lors des prêts
        """
        if amount_to_subtract > self.real_time_amount:
            raise ValueError("Le montant à soustraire dépasse l'épargne disponible")
        
        self.real_time_amount -= amount_to_subtract
        self.save()
        
        return self.real_time_amount
    
    def reset_real_time_amount(self):
        """
        Réinitialise le montant en temps réel à son montant de base
        """
        self.real_time_amount = self.base_amount
        self.save()
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
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='refunds_operation_app')
    borrowing_id = models.ForeignKey('operationApp.Borrowing', on_delete=models.CASCADE, null=True, related_name='refunds_operation_app')
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL, null=True, related_name='refunds_operation_app')
    create_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE, related_name='refunds_operation_app')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    redistribution_details = models.JSONField(default=dict, blank=True, null=True)
    is_redistributed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            borrowing = self.borrowing_id
            borrowing.amount_paid += self.amount
            
            if borrowing.amount_paid >= borrowing.amount_to_pay:
                borrowing.state = True
            
            borrowing.save()
            
            if not self.is_redistributed:
                self.redistribute_refund()

    def redistribute_refund(self):
        if self.is_redistributed:
            return  # Éviter la double redistribution

        borrowing = self.borrowing_id

        # Total remboursé (proportionnellement au montant total dû)
        payment_ratio = float(self.amount) / float(borrowing.amount_to_pay)

        # Initialisation des détails de redistribution
        redistribution_details = {}

        for member_id, initial_contribution in borrowing.loan_distribution.items():
            # Contribution proportionnelle au remboursement
            capital_return = float(initial_contribution) * payment_ratio

            # Part des intérêts pour ce membre
            interest_share = float(borrowing.interest) * (float(initial_contribution) / float(borrowing.amount_borrowed))

            # Total à restituer (capital + intérêts)
            total_return = capital_return + (interest_share * payment_ratio)

            # Mise à jour de l'épargne du membre
            member = Member.objects.get(id=int(member_id))
            savings = Epargne.objects.filter(
                member_id=member,
                session_id=self.session_id
            ).first()

            if savings:
                old_amount = savings.real_time_amount
                savings.real_time_amount += Decimal(total_return)
                savings.save()

                # Ajout des détails pour le suivi
                redistribution_details[member_id] = {
                    'capital_return': float(capital_return),
                    'interest_share': float(interest_share * payment_ratio),
                    'total_return': float(total_return)
                }

                # Créer une trace de redistribution
                RefundDistributionTrace.objects.create(
                    epargne=savings,
                    refund=self,
                    benefit_share=total_return,
                    real_time_amount_before=old_amount,
                    real_time_amount_after=savings.real_time_amount
                )

        # Mise à jour du remboursement avec les détails de redistribution
        self.is_redistributed = True
        self.redistribution_details = redistribution_details
        super().save(update_fields=['is_redistributed', 'redistribution_details'])

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
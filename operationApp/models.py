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
    date = models.CharField(max_length=20)
    help_id = models.ForeignKey('operationApp.Help', on_delete=models.SET_NULL,null=True) #l'aide en question
    amount = models.IntegerField(default=0)
    def __str__(self):
        return f"Contribution Personnelle de {self.member_id.username} pour l'aide a {self.help_id.member_id.username}"

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
    # Champs existants conservés
    interest = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_borrowed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_date_line = models.DateTimeField(blank=True, null=True)
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='borrowings_from_operation')
    state = models.BooleanField(default=False)
    
    # #modification: Ajout d'un champ pour suivre la répartition du prêt
    loan_distribution = models.JSONField(default=dict, blank=True, null=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Calcul de l'intérêt et du montant à payer
        if self.amount_borrowed is not None:
            self.interest = Decimal(float(self.amount_borrowed) * 0.05)
            self.amount_to_pay = self.amount_borrowed + self.interest
            
            # #modification: Définition de la date limite de paiement
            if not self.payment_date_line:
                self.payment_date_line = timezone.now() + timedelta(days=30)
            
            # #modification: Répartition du prêt entre les membres épargnants
            self.distribute_loan()
        
        super().save(*args, **kwargs)
    
    def distribute_loan(self):
        # Récupérer tous les membres épargnants actifs
        from members.models import Member
        active_members = Member.objects.filter(active=True)
        total_members = active_members.count()
        
        if total_members == 0:
            raise ValidationError("Aucun membre actif pour répartir le prêt")
        
        # Montant par membre
        amount_per_member = self.amount_borrowed / total_members
        
        # Initialisation du dictionnaire de répartition
        self.loan_distribution = {}
        
        # Variables pour gérer le reste du prêt
        remaining_amount = self.amount_borrowed
        
        for member in active_members:
            # Calcul de l'épargne réelle du membre
            member_savings = member.calculate_total_savings()
            
            if member_savings > 0:
                # Si le membre a suffisamment d'épargne
                if member_savings >= amount_per_member:
                    contribution = amount_per_member
                else:
                    # Prendre toute son épargne et répartir le reste
                    contribution = member_savings
                
                # Mettre à jour l'épargne du membre
                self.update_member_savings(member, contribution)
                
                # Enregistrer la contribution dans la distribution
                self.loan_distribution[str(member.id)] = float(contribution)
                
                remaining_amount -= contribution
            
        # Gérer le montant résiduel si nécessaire
        if remaining_amount > 0:
            self.handle_remaining_loan(remaining_amount)
        
        return self.loan_distribution
    
    def update_member_savings(self, member, amount):
        # Récupérer l'épargne du membre pour la session courante
        from operationApp.models import Epargne
        current_session = self.session_id
        
        # Trouver l'épargne du membre
        savings = Epargne.objects.filter(
            member_id=member, 
            session_id=current_session
        ).first()
        
        if savings:
            # Réduire le montant temps réel
            savings.real_time_amount -= amount
            
            # Enregistrer une trace de l'utilisation de l'épargne
            LoanUtilizationTrace.objects.create(
                epargne=savings,
                borrowing=self,
                amount_used=amount,
                real_time_amount_before=savings.real_time_amount + amount,
                real_time_amount_after=savings.real_time_amount
            )
            
            savings.save()
    
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
    # Champs existants conservés
    member_id = models.ForeignKey(
        'members.Member', 
        on_delete=models.CASCADE,
        related_name='refunds_operation_app'  # Nom unique pour ce membre
    )
    borrowing_id = models.ForeignKey(
        'operationApp.Borrowing', 
        on_delete=models.CASCADE, 
        null=True,
        related_name='refunds_operation_app'  # Nom unique pour cet emprunt
    )
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.SET_NULL, null=True,
                                         
                                         related_name='refunds_operation_app')  # Nom unique pour cet administrateur
    create_at = models.DateTimeField(auto_now=True)
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE,
                                   related_name='refunds_operation_app')
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    
    redistribution_details = models.JSONField(default=dict, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Mise à jour de l'emprunt
        borrowing = self.borrowing_id
        borrowing.amount_paid += self.amount
        
        # Vérification du statut de remboursement
        if borrowing.amount_paid >= borrowing.amount_to_pay:
            borrowing.state = True
        
        borrowing.save()
        
        # Distribution des bénéfices
        self.redistribute_refund()
    
    def redistribute_refund(self):
        # Calcul des bénéfices (intérêts)
        borrowing = self.borrowing_id
        benefits = borrowing.interest
        
        # Récupération des épargnes de la session
        savings = Epargne.objects.filter(session_id=self.session_id)
        total_session_savings = sum(saving.amount for saving in savings)
        
        # Initialisation des détails de redistribution
        self.redistribution_details = {}
        
        # Distribution proportionnelle
        for saving in savings:
            saving_percentage = saving.amount / total_session_savings
            benefit_share = benefits * saving_percentage
            
            # Tracer l'évolution du montant temps réel
            old_real_time_amount = saving.real_time_amount
            saving.real_time_amount += benefit_share
            saving.save()
            
            # Créer une trace de redistribution
            RefundDistributionTrace.objects.create(
                epargne=saving,
                refund=self,
                benefit_share=benefit_share,
                real_time_amount_before=old_real_time_amount,
                real_time_amount_after=saving.real_time_amount
            )
            
            # Enregistrement des détails
            self.redistribution_details[str(saving.member_id.id)] = float(benefit_share)
        
        self.save()
        return self.redistribution_details

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
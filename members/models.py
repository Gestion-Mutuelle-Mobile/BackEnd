from django.db import models
from users.models import User
from administrators.models import Administrator
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class Member(models.Model):
    # Champs existants conservés
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.CASCADE)
    username = models.CharField(max_length=8, blank=True)
    active = models.BooleanField(default=True)
    
    # #modification: Ajout de champs pour suivre la santé financière
    total_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_borrowings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inscription = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Mise à jour automatique du fonds social
        self.update_social_fund()
    
    def update_social_fund(self):
        """
        Mise à jour du fonds social lors de chaque sauvegarde du membre
        """
        from mutualApp.models import Session, FondSocial
        
        session = Session.objects.filter(active=True).first()
        if session:
            fond_social, created = FondSocial.objects.get_or_create(
                session_id=session, 
                defaults={'amount': self.inscription}
            )
            
            if not created:
                fond_social.update_fonds_social()
    
    def can_borrow(self, amount):
        """
        Vérifie si le membre peut emprunter un montant donné
        """
        total_savings = self.calculate_total_savings()
        max_borrowing = total_savings * 2  # Limite d'emprunt à deux fois l'épargne
        
        return amount <= max_borrowing and not self.has_late_borrowings()
    
    def has_late_borrowings(self):
        from operationApp.models import Borrowing

        """
        Vérifie si le membre a des emprunts en retard
        """
        return Borrowing.objects.filter(
            member_id=self, 
            state=False,  # Emprunt non remboursé
            payment_date_line__lt=timezone.now()  # Date limite dépassée
        ).exists()
    
    def calculate_borrowing_capacity(self):
        """
        Calcule la capacité d'emprunt du membre
        """
        total_savings = self.calculate_total_savings()
        return total_savings * 2


    def calculate_debt(self):
        """
        Calcule le montant total restant à rembourser par le membre.
        Somme de (amount_to_pay - amount_paid) pour tous les emprunts actifs.
        """
        total_debt = self.borrowing_set.aggregate(
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
            return Epargne.objects.filter(member_id=self, session_id=session).aggregate(
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
        tresorerie = Tresorerie.objects.filter(session_id=session).first()

        if tresorerie and tresorerie.amount > 0:
            return (Decimal(total_savings) / tresorerie.amount) * 100
        return Decimal(0)

    def __str__(self):
        return f"MEMBRE : {self.username} (ID: {self.user_id})"


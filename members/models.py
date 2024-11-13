from django.db import models
from users.models import User
from administrators.models import Administrator
# Create your models here.
class Member(models.Model):
    # id = models.IntegerField(max_length=10)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    username = models.CharField(max_length=8,  blank=True)

    active = models.BooleanField(default=True)
    social_crown = models.IntegerField(default=0)
    inscription = models.IntegerField(default=10000)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.CASCADE)

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

    def calculate_savings(self):
        """
        Calcule le montant total de l'épargne du membre (somme des remboursements).
        """
        total_savings = self.refund_set.aggregate(
            savings=models.Sum('amount')
        )['savings'] or 0
        return total_savings

    def __str__(self):
        return f"MEMBRE : {self.username} (ID: {self.user_id})"

    def __str__(self):
        return f"{self.username} (ID: {self.user_id})"
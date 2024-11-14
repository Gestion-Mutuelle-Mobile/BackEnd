from django.db import models
from members.models import Member
from administrators.models import Administrator


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



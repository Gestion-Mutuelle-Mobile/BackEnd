from django.db import models
from operationApp.models import Epargne

# Create your models here.
class Borrowing_Saving(models.Model):
    # id = models.IntegerField(max_length=10)
    borrowing_id = models.ForeignKey('operationApp.Borrowing', on_delete=models.CASCADE,null=True)
    epargne_id = models.ForeignKey('operationApp.Epargne', on_delete=models.CASCADE,null=True)
    percent = models.FloatField(max_length=10)

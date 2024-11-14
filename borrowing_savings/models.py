from django.db import models
from operationApp.models import Epargne

# Create your models here.
class Borrowing_Saving(models.Model):
    # id = models.IntegerField(max_length=10)
    borrowing_id = models.ForeignKey('operationApp.Borrowing', on_delete=models.CASCADE)
    saving_id = models.ForeignKey('borrowing_savings.Epargne', on_delete=models.CASCADE)
    percent = models.FloatField(max_length=10)

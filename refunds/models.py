from django.db import models
from operationApp.models import Borrowing
from members.models import Member
from administrators.models import Administrator
from mutualApp.models import Exercise
from mutualApp.models import Session
# Create your models here.
class Refund(models.Model):
    # id = models.IntegerField(max_length=10)
    amount = models.IntegerField()
    # borrowing_id = models.ForeignKey('borrowings.Borrowing', on_delete=models.CASCADE)
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.CASCADE,related_name='refunds_from_refunds')
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE, default=1,related_name='refunds_from_refunds')
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE,related_name='refunds_from_refunds')
    borrowing_id = models.ForeignKey('operationApp.Borrowing', on_delete=models.CASCADE,null=True,related_name='refunds_from_refunds')
    create_at = models.DateTimeField(auto_now_add=True)

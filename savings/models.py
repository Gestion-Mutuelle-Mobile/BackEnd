from django.db import models
from members.models import Member
from administrators.models import Administrator
from  mutualApp.models import Session
class Epargne(models.Model):
    # id = models.IntegerField(max_length=10)
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE,related_name='epargne_from_savings')
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.CASCADE)
    amount = models.IntegerField()
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now=True)

from django.db import models
from members.models import Member
from administrators.models import Administrator
from  mutualApp.models import Session
class Obligatory_Contribution(models.Model):
    # id = models.IntegerField(max_length=10)
    member_id = models.ForeignKey('members.Member', on_delete=models.CASCADE,related_name='obligatory_contribution_from_obligatory_contribution')
    administrator_id = models.ForeignKey('administrators.Administrator', on_delete=models.CASCADE)
    contributed = models.IntegerField(default=0)
    session_id = models.ForeignKey('mutualApp.Session', on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

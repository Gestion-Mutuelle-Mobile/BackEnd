from django.db import models
from administrators.models import Administrator
from mutualApp.models import Operation
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone


# Create your models here.
# class Exercise(Operation):
#     active = models.BooleanField(default=True)
#     create_at = models.DateTimeField(auto_now=True)
#     def update_active(self):
#         """
#         Met à jour le champ 'active' à False si l'exercice a été créé il y a plus d'un an.
#         """
#         one_year_ago = timezone.now() - timedelta(days=365)
#         if self.create_at < one_year_ago:
#             self.active = False
#             self.save()

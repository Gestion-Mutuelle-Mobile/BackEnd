from rest_framework import serializers

from mutualApp.models import Session
from operationApp.models import ObligatoryContribution
from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

    def get_total_debt(self, obj):
        # Appelle la méthode calculate_debt de Member pour obtenir le total restant à rembourser
        return obj.calculate_debt()

    def get_has_open_help(self, obj):
        return obj.has_open_help()

    def get_total_savings(self, obj):
        return obj.calculate_savings()

    def get_has_contributed(self, obj):
        """
        Vérifie si le membre a payé sa contribution obligatoire pour la session active la plus récente.
        """
        session = Session.objects.filter(active=True).order_by('-create_at').first()
        if session:
            return ObligatoryContribution.objects.filter(
                member_id=obj, session=session, contributed=True
            ).exists()
        return False
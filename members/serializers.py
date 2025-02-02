from rest_framework import serializers

from mutualApp.models import Session
from operationApp.models import ObligatoryContribution
from users.serializers import UserSerializer
from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='user_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur
    has_open_help = serializers.SerializerMethodField()
    total_savings = serializers.SerializerMethodField()  # Champ pour total_savings
    has_contributed = serializers.SerializerMethodField()
    total_debt = serializers.SerializerMethodField()
    calculate_total_savings= serializers.SerializerMethodField()
    tresorerie_percentage= serializers.SerializerMethodField()


    class Meta:
        model = Member
        fields = '__all__'

    def get_total_debt(self, obj):
        # Appelle la méthode calculate_debt de Member pour obtenir le total restant à rembourser
        return obj.calculate_debt()

    def get_has_open_help(self, obj):
        return False

    def get_total_savings(self, obj):
        return obj.calculate_total_savings()

    def get_has_contributed(self, obj):
        """
        Vérifie si le membre a payé sa contribution obligatoire pour la session active la plus récente.
        """
        session = Session.objects.filter(active=True).order_by('-create_at').first()
        if session:
            return ObligatoryContribution.objects.filter(
                member_id=obj, session_id=session, contributed=True
            ).exists()
        return False
    def get_calculate_total_savings(self,obj):
        return obj.get_current_savings()
    def get_get_current_savings(self, obj):
        return obj.get_current_savings()  # Utilise la méthode du modèle
    def get_tresorerie_percentage(self,obj):
        return obj.calculate_tresorerie_percentage()
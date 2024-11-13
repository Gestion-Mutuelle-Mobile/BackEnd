from rest_framework import serializers
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
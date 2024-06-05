from members.models import Member
from rest_framework import viewsets, permissions
from .serializers import MemberSerializer

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = MemberSerializer
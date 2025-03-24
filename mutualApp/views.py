from mutualApp.models import Exercise
from rest_framework import viewsets, permissions
from mutualApp.serializers import *
from mutualApp.models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ExerciseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par tout

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SessionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par tout



# ViewSet pour FondSocial
class FondSocialViewSet(viewsets.ModelViewSet):
    queryset = FondSocial.objects.all()
    serializer_class = FondSocialSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par tout
    


# ViewSet pour Tresorerie
class TresorerieViewSet(viewsets.ModelViewSet):
    queryset = Tresorerie.objects.all()
    serializer_class = TresorerieSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par tout


# Vue pour retirer une somme du FondSocial de la session active la plus récente
class SubstractFondSocialView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Le montant est requis."}, status=status.HTTP_400_BAD_REQUEST)

        # Trouver la session active la plus récente
        session = Session.objects.filter(active=True).order_by('-create_at').first()
        if not session:
            return Response({"error": "Aucune session active trouvée."}, status=status.HTTP_404_NOT_FOUND)

        # Retirer le montant du fond social de cette session
        fond_social = FondSocial.objects.filter(session=session).first()
        if not fond_social:
            return Response({"error": "FondSocial non trouvé pour la session active."}, status=status.HTTP_404_NOT_FOUND)

        # Appliquer le retrait
        fond_social.substract(float(amount))
        serializer = FondSocialSerializer(fond_social)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Vue pour retirer une somme de la Tresorerie de la session active la plus récente
class SubstractTresorerieView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Le montant est requis."}, status=status.HTTP_400_BAD_REQUEST)

        # Trouver la session active la plus récente
        session = Session.objects.filter(active=True).order_by('-create_at').first()
        if not session:
            return Response({"error": "Aucune session active trouvée."}, status=status.HTTP_404_NOT_FOUND)

        # Retirer le montant de la trésorerie de cette session
        tresorerie = Tresorerie.objects.filter(session=session).first()
        if not tresorerie:
            return Response({"error": "Tresorerie non trouvée pour la session active."}, status=status.HTTP_404_NOT_FOUND)

        # Appliquer le retrait
        tresorerie.substract(float(amount))
        serializer = TresorerieSerializer(tresorerie)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class AddTresorerieView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Le montant est requis."}, status=status.HTTP_400_BAD_REQUEST)

        # Trouver la session active la plus récente
        session = Session.objects.filter(active=True).order_by('-create_at').first()
        if not session:
            return Response({"error": "Aucune session active trouvée."}, status=status.HTTP_404_NOT_FOUND)

        # Retirer le montant de la trésorerie de cette session
        tresorerie = Tresorerie.objects.filter(session=session).first()
        if not tresorerie:
            return Response({"error": "Tresorerie non trouvée pour la session active."}, status=status.HTTP_404_NOT_FOUND)

        # Appliquer le retrait
        tresorerie.addAmmount(float(amount))
        serializer = TresorerieSerializer(tresorerie)
        return Response(serializer.data, status=status.HTTP_200_OK)
from django.urls import path
from rest_framework import routers
from mutualApp.views import *
from rest_framework.urlpatterns import format_suffix_patterns  # Importation pour gérer les suffixes de format

router = routers.DefaultRouter()
router.register('api/exercises', ExerciseViewSet, 'exercises')
router.register('api/sessions_', SessionViewSet, 'sessions_')
router.register('api/fond_social', FondSocialViewSet, 'fond_social')
router.register('api/tresorerie', TresorerieViewSet, 'tresorerie')

# Liste des URLs de l'API
urlpatterns = [
    path('fondsocial/substract/', SubstractFondSocialView.as_view(), name='substract_fond_social'),
    path('tresorerie/substract/', SubstractTresorerieView.as_view(), name='substract_tresorerie'),
] + router.urls  # Ajoute les URLs générées par le router

# Ajoute la gestion des formats (suffixes)
urlpatterns = format_suffix_patterns(urlpatterns)

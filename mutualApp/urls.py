from django.urls import path
from rest_framework import routers
from mutualApp.views import *

router = routers.DefaultRouter()
router.register('api/exercises',ExerciseViewSet,'exercises')
router.register('api/sessions_',SessionViewSet,'sessions_')
router.register('api/fond_social',FondSocialViewSet,'fond_social')
router.register('api/tresorerie',TresorerieViewSet,'tresorerie')

urlpatterns = [router.urls,
    path('fondsocial/substract/', SubstractFondSocialView.as_view(), name='substract_fond_social'),
    path('tresorerie/substract/', SubstractTresorerieView.as_view(), name='substract_tresorerie'),
]
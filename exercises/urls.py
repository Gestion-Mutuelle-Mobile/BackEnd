from rest_framework import routers
from mutualApp.views import ExerciseViewSet

router = routers.DefaultRouter()
# router.register('api/exercises',ExerciseViewSet,'exercises')
urlpatterns = router.urls

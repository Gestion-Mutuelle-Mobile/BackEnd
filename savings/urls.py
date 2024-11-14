from rest_framework import routers
from .api import EpargneViewSet

router = routers.DefaultRouter()
router.register('api/savings', EpargneViewSet, 'savings')
urlpatterns = router.urls

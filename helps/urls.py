from rest_framework import routers
from .api import HelpViewSet

router = routers.DefaultRouter()
router.register('api/helps_v1',HelpViewSet,'helps')
urlpatterns = router.urls

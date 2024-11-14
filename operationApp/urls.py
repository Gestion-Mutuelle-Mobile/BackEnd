from rest_framework import routers
from .views import  *
router = routers.DefaultRouter()
router.register('api/contributions',PersonalContributionViewSet,'contributions')
router.register('api/helps',HelpViewSet,'helps')

urlpatterns = router.urls

from rest_framework import routers

from operationApp.views import BorrowingViewSet


router = routers.DefaultRouter()
router.register('api/borrowings',BorrowingViewSet,'borrowings')
urlpatterns = router.urls

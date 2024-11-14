from django.urls import path
from rest_framework import routers
from .views import  *
router = routers.DefaultRouter()
router.register('api/contributions',PersonalContributionViewSet,'contributions')
router.register('api/helps',HelpViewSet,'helps')
router.register('api/obligatory_contributions',Obligatory_ContributionViewSet,'obligatory_contributions')
router.register('api/borrowings',BorrowingViewSet,'borrowings')
router.register('api/savings', EpargneViewSet, 'savings')
router.register('api/refunds',RefundViewSet,'refunds')

urlpatterns = [
    path('help/close/<int:pk>/', CloseHelpView.as_view(), name='close_help')
]+ router.urls

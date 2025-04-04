from django.urls import path
from rest_framework import routers
from .api import MemberViewSet, UnpaidObligatoryContributionMembersViewSet, RegisterUserView

router = routers.DefaultRouter()
router.register('api/members',MemberViewSet,'members')
router.register('api/obligatory_contributions/unpaid', UnpaidObligatoryContributionMembersViewSet, 'unpaid-members')

urlpatterns = [
    path('api/register/', RegisterUserView.as_view(), name='register_user'),
]+router.urls

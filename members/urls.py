from django.urls import path
from rest_framework import routers
from .api import MemberViewSet, UnpaidObligatoryContributionMembersViewSet, RegisterUserView, ImportMembersFromExcel
from .views import AllNotificationsView, register_token,send_notification, send_notification_All

router = routers.DefaultRouter()
router.register('api/members',MemberViewSet,'members')
router.register('api/obligatory_contributions/unpaid', UnpaidObligatoryContributionMembersViewSet, 'unpaid-members')


urlpatterns = [
    path('api/register/', RegisterUserView.as_view(), name='register_user'),
    path('api/import-members/', ImportMembersFromExcel.as_view(), name='import_members'),
    path("api/register-token/", register_token, name="register_token"),
    path('api/notifications/', AllNotificationsView.as_view(), name='All-notifications'),
    path('api/notifications/send/',send_notification, name='Send_notifications'),
    path('api/notifications/send_All/',send_notification_All, name='Send_all_notifications'),
]+router.urls

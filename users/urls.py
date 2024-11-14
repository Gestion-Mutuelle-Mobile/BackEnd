from rest_framework import routers
from .api import UserViewSet
from django.urls import path
from .views import VerifyPasswordView
router = routers.DefaultRouter()
router.register('api/users',UserViewSet,'users')
urlpatterns = [
    path('verify-password/', VerifyPasswordView.as_view(), name='verify_password'),
]+router.urls

#com
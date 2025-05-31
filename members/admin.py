from django.contrib import admin

from members.models import Member
from .models import DeviceToken, Notification

# Affichage dans l'admin pour DeviceToken
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')

admin.site.register(DeviceToken, DeviceTokenAdmin)

# Affichage dans l'admin pour Member
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass

# Affichage dans l'admin pour Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('user__username', 'title', 'body')

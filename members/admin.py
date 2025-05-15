from django.contrib import admin

from members.models import Member

from .models import DeviceToken

class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')  # Ce que tu veux afficher dans l'admin

admin.site.register(DeviceToken, DeviceTokenAdmin)
# Register your models here.
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass


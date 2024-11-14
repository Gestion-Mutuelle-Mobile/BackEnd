from django.contrib import admin

from administrators.models import Administrator


# Register your models here.
@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    pass
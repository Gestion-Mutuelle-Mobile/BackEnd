from django.contrib import admin

from operationApp.models import Operation, Contribution, PersonalContribution, Help


# Register your models here.
@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    pass


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonalContribution)
class PersonalContributionAdmin(admin.ModelAdmin):
    pass


@admin.register(Help)
class HelpAdmin(admin.ModelAdmin):
    pass
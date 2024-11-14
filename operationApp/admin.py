from django.contrib import admin

from operationApp.models import Operation, Contribution, PersonalContribution, Help, ObligatoryContribution, Borrowing, \
    Epargne, Refund


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


@admin.register(ObligatoryContribution)
class Obligatory_ContributionAdmin(admin.ModelAdmin):
    pass


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    pass


@admin.register(Epargne)
class EpargneAdmin(admin.ModelAdmin):
    pass


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    pass
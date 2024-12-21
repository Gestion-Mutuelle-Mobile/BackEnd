from django.contrib import admin

from operationApp.models import *


# Register your models here.
@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'administrator_id', 'create_at', 'session_id')  # Champs visibles
    readonly_fields = ('create_at',)


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
    list_display = ('id', 'interest', 'amount_borrowed', 'payment_date_line', 'create_at')  # Champs visibles
    readonly_fields = ('payment_date_line', 'create_at')


@admin.register(Epargne)
class EpargneAdmin(admin.ModelAdmin):
    pass


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    pass

@admin.register(LoanUtilizationTrace)
class LoanUtilizationTraceAdmin(admin.ModelAdmin):
    pass

@admin.register(RefundDistributionTrace)
class RefundDistributionTraceAdmin(admin.ModelAdmin):
    pass
from django.contrib import admin

from operationApp.models import *


from django.contrib import admin
from operationApp.models import *
from django.utils.html import format_html
from django.urls import reverse

class BaseAdmin(admin.ModelAdmin):
    """Classe de base pour les configurations admin communes"""
    list_per_page = 20
    date_hierarchy = 'create_at'
    list_filter = ('session_id', 'create_at')
    search_fields = ('id', 'member_id__username', 'administrator_id__username')
    
    def get_member_link(self, obj):
        if obj.member_id:
            url = reverse('admin:members_member_change', args=[obj.member_id.id])
            return format_html('<a href="{}">{}</a>', url, obj.member_id.username)
        return "-"
    get_member_link.short_description = "Membre"

    def get_admin_link(self, obj):
        if obj.administrator_id:
            url = reverse('admin:administrators_administrator_change', args=[obj.administrator_id.id])
            return format_html('<a href="{}">{}</a>', url, obj.administrator_id.username)
        return "-"
    get_admin_link.short_description = "Administrateur"

@admin.register(Operation)
class OperationAdmin(BaseAdmin):
    list_display = ('id', 'get_admin_link', 'create_at', 'session_id')
    readonly_fields = ('create_at',)

@admin.register(Contribution)
class ContributionAdmin(BaseAdmin):
    list_display = ('id', 'get_member_link', 'state', 'get_admin_link', 'create_at', 'session_id')
    list_editable = ('state',)
    readonly_fields = ('create_at',)

@admin.register(PersonalContribution)
class PersonalContributionAdmin(ContributionAdmin):
    list_display = ('id', 'amount', 'get_help_link', 'state', 'create_at')
    list_filter = ContributionAdmin.list_filter + ('help_id',)
    
    def get_help_link(self, obj):
        if obj.help_id:
            url = reverse('admin:operationApp_help_change', args=[obj.help_id.id])
            return format_html('<a href="{}">{}</a>', url, str(obj.help_id))
        return "-"
    get_help_link.short_description = "Aide"

@admin.register(Help)
class HelpAdmin(BaseAdmin):
    list_display = ('id', 'get_member_link', 'amount_expected', 'limit_date', 'state', 'create_at')
    list_editable = ('state',)
    readonly_fields = ('create_at',)
    search_fields = BaseAdmin.search_fields + ('comments',)
    list_filter = BaseAdmin.list_filter + ('state', 'limit_date')

@admin.register(ObligatoryContribution)
class ObligatoryContributionAdmin(ContributionAdmin):
    list_display = ('id', 'get_member_link', 'amount', 'contributed', 'state', 'create_at')
    list_editable = ('contributed', 'state')
    list_filter = ContributionAdmin.list_filter + ('contributed',)

@admin.register(Borrowing)
class BorrowingAdmin(BaseAdmin):
    list_display = ('id', 'get_member_link', 'amount_borrowed', 'amount_paid', 'interest', 
                   'payment_date_line', 'state', 'create_at')
    list_editable = ('state',)
    readonly_fields = ('payment_date_line', 'create_at')
    fieldsets = (
        ('Informations principales', {
            'fields': ('member_id', 'amount_borrowed', 'amount_paid', 'state')
        }),
        ('Détails financiers', {
            'fields': ('interest', 'amount_to_pay', 'payment_date_line')
        }),
        ('Informations système', {
            'fields': ('administrator_id', 'session_id', 'create_at', 'loan_distribution')
        }),
    )

@admin.register(Epargne)
class EpargneAdmin(BaseAdmin):
    list_display = ('id', 'get_member_link', 'amount', 'base_amount', 'real_time_amount', 'create_at')
    readonly_fields = ('base_amount', 'create_at')
    fieldsets = (
        ('Informations principales', {
            'fields': ('member_id', 'amount')
        }),
        ('Montants calculés', {
            'fields': ('base_amount', 'real_time_amount')
        }),
        ('Informations système', {
            'fields': ('administrator_id', 'session_id', 'create_at')
        }),
    )

@admin.register(Refund)
class RefundAdmin(BaseAdmin):
    list_display = ('id', 'get_member_link', 'get_borrowing_link', 'amount', 'create_at')
    readonly_fields = ('create_at', 'redistribution_details')
    
    def get_borrowing_link(self, obj):
        if obj.borrowing_id:
            url = reverse('admin:operationApp_borrowing_change', args=[obj.borrowing_id.id])
            return format_html('<a href="{}">{}</a>', url, f"Emprunt #{obj.borrowing_id.id}")
        return "-"
    get_borrowing_link.short_description = "Emprunt"

@admin.register(LoanUtilizationTrace)
class LoanUtilizationTraceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_epargne_link', 'get_borrowing_link', 'amount_used', 
                   'real_time_amount_before', 'real_time_amount_after', 'created_at')
    readonly_fields = ('created_at',)
    
    def get_epargne_link(self, obj):
        url = reverse('admin:operationApp_epargne_change', args=[obj.epargne.id])
        return format_html('<a href="{}">{}</a>', url, f"Épargne #{obj.epargne.id}")
    get_epargne_link.short_description = "Épargne"
    
    def get_borrowing_link(self, obj):
        url = reverse('admin:operationApp_borrowing_change', args=[obj.borrowing.id])
        return format_html('<a href="{}">{}</a>', url, f"Emprunt #{obj.borrowing.id}")
    get_borrowing_link.short_description = "Emprunt"

@admin.register(RefundDistributionTrace)
class RefundDistributionTraceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_epargne_link', 'get_refund_link', 'benefit_share',
                   'real_time_amount_before', 'real_time_amount_after', 'created_at')
    readonly_fields = ('created_at',)
    
    def get_epargne_link(self, obj):
        url = reverse('admin:operationApp_epargne_change', args=[obj.epargne.id])
        return format_html('<a href="{}">{}</a>', url, f"Épargne #{obj.epargne.id}")
    get_epargne_link.short_description = "Épargne"
    
    def get_refund_link(self, obj):
        url = reverse('admin:operationApp_refund_change', args=[obj.refund.id])
        return format_html('<a href="{}">{}</a>', url, f"Remboursement #{obj.refund.id}")
    get_refund_link.short_description = "Remboursement"
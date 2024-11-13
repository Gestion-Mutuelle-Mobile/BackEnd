from django.contrib import admin

from mutualApp.models import Exercise, Session, FondSocial, Tresorerie


# Register your models here.
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    pass


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass


@admin.register(FondSocial)
class FondSocialAdmin(admin.ModelAdmin):
    pass


@admin.register(Tresorerie)
class TresorerieAdmin(admin.ModelAdmin):
    pass
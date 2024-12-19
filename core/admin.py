from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserRestriction

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'

class UserRestrictionInline(admin.TabularInline):
    model = UserRestriction
    fk_name = 'user'
    extra = 0
    readonly_fields = ('start_date', 'end_date')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, UserRestrictionInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_group', 'is_staff')
    list_filter = BaseUserAdmin.list_filter + ('groups__name',)
    
    def get_group(self, obj):
        if obj.is_superuser:
            return 'Administrador'
        return obj.groups.first().name if obj.groups.exists() else 'Sin grupo'
    get_group.short_description = 'Grupo'
    get_group.admin_order_field = 'groups__name'

@admin.register(UserRestriction)
class UserRestrictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'restriction_type', 'duration_days', 'start_date', 'end_date', 'is_active', 'restricted_by')
    list_filter = ('restriction_type', 'duration_days', 'start_date')
    search_fields = ('user__username', 'restricted_by__username', 'reason')
    readonly_fields = ('start_date', 'end_date')
    raw_id_fields = ('user', 'restricted_by')

# Re-registrar el modelo User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

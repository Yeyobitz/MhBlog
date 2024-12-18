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
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = BaseUserAdmin.list_filter + ('profile__role',)
    
    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Rol'
    get_role.admin_order_field = 'profile__role'

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

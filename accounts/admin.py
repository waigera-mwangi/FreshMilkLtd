from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ngettext

from .models import User, FarmerProfile, FinanceProfile, FieldProfile, ManagerProfile, VeterinaryProfile
from .forms import UserAdminChangeForm, RegistrationForm

# -------------------
# Customize Admin Site Header
# -------------------
admin.site.site_header = "Fresh Milk Ltd ADMIN"
admin.site.site_title = "Fresh Milk Ltd Admin Portal"
admin.site.index_title = "Welcome to Fresh Milk Ltd Management Portal"

# Unregister default Groups
admin.site.unregister(Group)

# -------------------
# Custom User Admin
# -------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = RegistrationForm

    list_display = ('username', 'email', 'user_type', 'is_active', 'is_archived')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_archived', 'user_type')
    actions = ['make_active', 'make_inactive']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'town', 'location')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'username', 'user_type', 'password1', 'password2'),
        }),
    )

    ordering = ['username']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True, is_archived=False)
        self.message_user(request, ngettext(
            '%d user was successfully marked as active.',
            '%d users were successfully marked as active.',
            updated,
        ) % updated, messages.SUCCESS)

    make_active.short_description = "Activate Selected Users"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False, is_archived=True)
        self.message_user(request, ngettext(
            '%d user was archived successfully.',
            '%d users were archived successfully.',
            updated,
        ) % updated, messages.INFO)

    make_inactive.short_description = "Archive Selected Users"


# -------------------
# Profile Admin Classes
# -------------------
class BaseProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gender', 'is_active')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('gender', 'is_active')


# -------------------
# Profiles under "Profiles" App Label
# -------------------
# admin.site.register(FarmerProfile, BaseProfileAdmin)
# admin.site.register(FinanceProfile, BaseProfileAdmin)
# admin.site.register(FieldProfile, BaseProfileAdmin)
# admin.site.register(ManagerProfile, BaseProfileAdmin)
# admin.site.register(VeterinaryProfile, BaseProfileAdmin)

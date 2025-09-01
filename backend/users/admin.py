from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, EventClient


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the User model."""
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(EventClient)
class EventClientAdmin(admin.ModelAdmin):
    """Admin configuration for the EventClient model."""
    list_display = ('name', 'email', 'phone_number', 'created_at')
    search_fields = ('name', 'email', 'phone_number')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
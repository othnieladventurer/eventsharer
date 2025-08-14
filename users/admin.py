from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser, Trial


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'profile_picture', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)





@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ("user", "start_date", "end_date", "is_active_status")
    list_filter = ("start_date", "end_date")
    search_fields = ("user__email",)

    def is_active_status(self, obj):
        return obj.is_active
    is_active_status.boolean = True  # Shows as ✅/❌
    is_active_status.short_description = "Active?"

    # Optional: make trial read-only if it has ended
    def get_readonly_fields(self, request, obj=None):
        if obj and not obj.is_active:
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)











from django.contrib import admin
from .models import *

admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'uuid', 'created_at')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at',)

@admin.register(EventMedia)
class EventMediaAdmin(admin.ModelAdmin):
    list_display = ('event', 'media_type', 'get_uploaded_by_first_name', 'get_uploaded_by_last_name', 'uploaded_at')
    search_fields = ('event__title', 'uploaded_by__first_name', 'uploaded_by__last_name')
    list_filter = ('media_type', 'uploaded_at')

    def get_uploaded_by_first_name(self, obj):
        return obj.uploaded_by.first_name if obj.uploaded_by else ''
    get_uploaded_by_first_name.short_description = 'Uploaded By First Name'

    def get_uploaded_by_last_name(self, obj):
        return obj.uploaded_by.last_name if obj.uploaded_by else ''
    get_uploaded_by_last_name.short_description = 'Uploaded By Last Name'

    

@admin.register(EventInvitee)
class EventInviteeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'event', 'token', 'created_at')
    search_fields = ('first_name', 'last_name', 'event__title')
    readonly_fields = ('token', 'created_at')
    list_filter = ('event', 'created_at')

admin.site.register(SubscriptionSession)





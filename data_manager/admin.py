from django.contrib import admin
from .models import Dataset, DataColumn, MetabaseConfig, MetabaseDashboard, UserActivity

admin.site.register(Dataset)
admin.site.register(DataColumn)

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'dataset', 'dashboard', 'timestamp')
    list_filter = ('action', 'user', 'timestamp')
    search_fields = ('user__username', 'dataset__name', 'dashboard__title')
    date_hierarchy = 'timestamp'
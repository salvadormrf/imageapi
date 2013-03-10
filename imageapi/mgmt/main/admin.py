from django.contrib import admin

from mgmt.main.models import Page, Placeholder


class PlaceholderInline(admin.TabularInline):
    model = Placeholder


class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "placeholders")
    inlines = [PlaceholderInline]
    
    def placeholders(self, obj):
        return obj.placeholder_set.count()
    

admin.site.register(Page, PageAdmin)

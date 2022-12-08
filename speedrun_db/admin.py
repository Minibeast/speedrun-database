from django.contrib import admin

from .models import Game, Category, Run

class RunAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ['url_id']
        else:
            return []

admin.site.register(Game)
admin.site.register(Category)
admin.site.register(Run, RunAdmin)

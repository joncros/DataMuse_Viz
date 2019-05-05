from django.contrib import admin


class WordSetAdmin(admin.ModelAdmin):
    """Override ModelAdmin save_model to attach the user (if logged in) when adding a new WordSet"""
    def save_model(self, request, obj, form, change):
        if change is False:
            # only change if instance is being saved for the first time
            obj.creator = request.user
        super().save_model(request, obj, form, change)

from django.contrib import admin

from words.models import Language, Word, PartOfSpeech, WordSet

# register model classes so they are visible on admin site (admin/)
admin.site.register(Language)
admin.site.register(Word)
admin.site.register(PartOfSpeech)
admin.site.register(WordSet)


class WordSetAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """Override to attach the user (if logged in) when adding a new WordSet"""
        if change is False:
            # only change if instance is being saved for the first time
            obj.creator = request.user
        super().save_model(request, obj, form, change)

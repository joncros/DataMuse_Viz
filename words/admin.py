from django.contrib import admin

from words.models import Language, Word, PartOfSpeech, WordSet

# register model classes so they are visible on admin site (admin/)
admin.site.register(Language)
admin.site.register(Word)
admin.site.register(PartOfSpeech)
admin.site.register(WordSet)



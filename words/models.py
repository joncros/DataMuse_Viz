from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.contrib.auth.models import User
from django.db.models import BooleanField
from django.urls import reverse


class Language(models.Model):
    """Model representing a language supported by DataMuse (currently, English or Spanish"""

    # tuple holding available language choices. first item in each nested tuple is the ISO 639-1 code
    name_choices = (
        ('en', 'English'),
        ('es', 'Spanish'),
    )

    name = models.CharField(
        max_length=2,
        primary_key=True,
        unique=True,
        choices=name_choices,
        blank=False,
        help_text='Language',
    )

    def __str__(self):
        """String for representing the Model object"""
        return self.get_name_display()

    # todo method (may not belong in models) to add "v=name", if name not en, to DataMuse queries
    # todo setting or property somewhere to indicate DataMuse parameters not supported by a language


def default_language():
    lang = Language('en')
    lang.save()
    return lang.pk


class WordQuerySet(models.query.QuerySet):
    """Custom QuerySet converts name value to lowercase before searching.

    A search for an object with name='The' would return the object with name='the'."""
    def get(self, **kwargs):
        if kwargs['name']:
            kwargs['name'] = kwargs['name'].lower()
        return super().get(**kwargs)


class WordManager(models.Manager.from_queryset(WordQuerySet)):
    # use WordQuerySet for the manager
    pass


class Word(models.Model):
    """Model representing a word and its relationships to other words."""

    # Custom manager that converts name to lowercase before searching for the instance
    objects = WordManager()

    name = models.CharField(max_length=100)
    parts_of_speech = models.ManyToManyField('PartOfSpeech', blank=True)
    language = models.ForeignKey('Language', blank=False, default=default_language, on_delete=models.PROTECT)

    # number of occurrences per million words of english text
    frequency = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)

    # JSON returned from DataMuse containing one or more strings defining the word
    definitions = JSONField(null=True, blank=True)

    # flag indicates if DataMuse was successfully queried to fill parts_of_speech, frequency and definitions fields
    # purpose is to avoid redundant DataMuse queries
    datamuse_success = BooleanField(default=False)

    # Remaining fields hold words related to this word.
    # Field names derived from three-letter codes used by rel_[code] DataMuse parameter
    # todo all related word fields should have symmetrical=False so datamuse_json will not skip add_related until called once for a word
    jja = models.ManyToManyField('self', blank=True, verbose_name='popular related noun', symmetrical=False,
                                 related_name='related_by_jja')
    jjb = models.ManyToManyField('self', blank=True, verbose_name='popular related adjective', symmetrical=False,
                                 related_name='related_by_jjb')
    syn = models.ManyToManyField('self', blank=True, verbose_name='synonym', related_name='synonyms',
                                 related_query_name='synonym')

    # Words that are statistically associated with this word in the same piece of text
    trg = models.ManyToManyField('self', blank=True, verbose_name='triggers', symmetrical=False,
                                 related_name='words_is_trigger_for', related_query_name='is_trigger_for')

    ant = models.ManyToManyField('self', blank=True, verbose_name='antonyms', related_name='antonyms',
                                 related_query_name='antonym')
    spc = models.ManyToManyField('self', blank=True, verbose_name='direct hypernyms', symmetrical=False,
                                 help_text='words with a similar, but broader meaning '
                                           '(i.e. boat is a hypernym of gondola)',
                                 related_name='hyponyms', related_query_name='hyponym')
    gen = models.ManyToManyField('self', blank=True, verbose_name='direct hyponyms', symmetrical=False,
                                 help_text='words with a similar, but more specific meaning '
                                           '(i.e. gondola is a hyponym of boat)',
                                 related_name='hypernyms', related_query_name='hypernym')
    com = models.ManyToManyField('self', blank=True, verbose_name='comprises', symmetrical=False,
                                 help_text='things which this is composed of'
                                           '(a car has an accelerator, a steering wheel, etc.',
                                 related_name='part_of')
    par = models.ManyToManyField('self', blank=True, verbose_name='part of', symmetrical=False,
                                 help_text='things of which this is a part of'
                                           '(a window is a part of a car, a house, a boat, etc.)',
                                 related_name='comprises')
    bga = models.ManyToManyField('self', blank=True, verbose_name='frequent followers', symmetrical=False,
                                 help_text='words that frequently follow this '
                                           '(i.e. wreak followed by havoc',
                                 related_name='frequently_follows')
    bgb = models.ManyToManyField('self', blank=True, verbose_name='frequent predecessors', symmetrical=False,
                                 help_text='words that frequently precede this'
                                           '(i.e. havoc preceding wreak',
                                 related_name='frequently_precedes')
    rhy = models.ManyToManyField('self', blank=True, verbose_name='rhymes', help_text='perfect rhymes',
                                 related_name='rhymes', related_query_name='rhyme')
    nry = models.ManyToManyField('self', blank=True, verbose_name='near rhymes', help_text='approximate rhymes',
                                 related_name='near_rhymes', related_query_name='near_rhyme')
    hom = models.ManyToManyField('self', blank=True, verbose_name='homophones', help_text='sound-alike words',
                                 related_name='homophones', related_query_name='homophone')
    cns = models.ManyToManyField('self', blank=True, verbose_name='consonant matches', help_text='i.e. sample and simple',
                                 related_name='consonant_matches', related_query_name='consonant_match')

    class Meta:
        # for each language, there should be only one word with a certain name
        constraints = [models.UniqueConstraint(fields=['name', 'language'], name='unique_word_per_language'), ]

    def save(self, *args, **kwargs):
        self.name = self.name.lower()  # Convert name to lowercase
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        """String for representing the Model object"""
        return self.name


class PartOfSpeech(models.Model):
    """Model representing a part of speech (noun, verb, adjective, adverb or unknown."""

    # tuple uses abbreviations used by DataMuse
    part_choices = (
        ('n', 'noun'),
        ('v', 'verb'),
        ('adj', 'adjective'),
        ('adv', 'adverb'),
        # ('u', 'unknown'),  blank value in Word will indicate unknown instead of 'u'
    )

    name = models.CharField(
        primary_key=True,
        unique=True,
        max_length=3,
        choices=part_choices,
        help_text='Part of speech',
    )

    def __str__(self):
        """String for representing the Model object"""
        return self.get_name_display()


class WordSet(models.Model):
    """"A user-defined set of words that have something in common, such as appearing in a certain book."""
    name = models.CharField(max_length=100, help_text="Enter a unique name for this set of words")
    description = models.TextField(blank=True, help_text="Enter a description for this set of words")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    words = models.ManyToManyField(Word, related_name='words', related_query_name='word', blank=True)

    class Meta:
        # for each creator, there should only be one wordset with a given name
        constraints = [models.UniqueConstraint(fields=['name', 'creator'], name='unique_wordset_name_per_creator'), ]

    def get_absolute_url(self):
        """Returns the url to access a particular wordset instance."""
        return reverse('wordset-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object"""
        # if creator null, UniqueConstraint cannot be enforced; so identify wordset by name and id
        creator_string = f' ({self.id})'
        if self.creator is not None:
            creator_string = f' (created by {self.creator})'
        return f'{self.name}' + creator_string


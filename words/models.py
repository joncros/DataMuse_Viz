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
        if 'name' in kwargs:
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

    # Remaining fields hold words related to this word. The relationships are governed by the RelatedWords model class.
    # Field names derived from three-letter codes used by rel_[code] DataMuse parameter.
    # datamuse_json skips a related word DataMuse query if the field is already populated.
    jja = models.ManyToManyField('self', through='JJA', blank=True, verbose_name='popular related nouns',
                                 symmetrical=False, related_name='related_by_jja')
    jjb = models.ManyToManyField('self', through='JJB', blank=True, verbose_name='popular related adjectives',
                                 symmetrical=False, related_name='related_by_jjb')
    syn = models.ManyToManyField('self', through='SYN', blank=True, verbose_name='synonyms', symmetrical=False,
                                 related_name='related_by_syn')
    trg = models.ManyToManyField('self', through='TRG', blank=True, verbose_name='triggers', symmetrical=False,
                                 related_name='related_by_trg',
                                 help_text='words that are statistically associated with this word '
                                           'in the same piece of text')
    ant = models.ManyToManyField('self', through='ANT', blank=True, verbose_name='antonyms', symmetrical=False,
                                 related_name='related_by_ant')
    spc = models.ManyToManyField('self', through='SPC', blank=True, verbose_name='direct hypernyms', symmetrical=False,
                                 related_name='related_by_spc',
                                 help_text='words with a similar, but broader meaning '
                                           '(i.e. boat is a hypernym of gondola)')
    gen = models.ManyToManyField('self', through='GEN', blank=True, verbose_name='direct hyponyms', symmetrical=False,
                                 related_name='related_by_gen',
                                 help_text='words with a similar, but more specific meaning '
                                           '(i.e. gondola is a hyponym of boat)')
    com = models.ManyToManyField('self', through='COM', blank=True, verbose_name='comprises', symmetrical=False,
                                 related_name='related_by_com',
                                 help_text='things which this is composed of'
                                           '(a car has an accelerator, a steering wheel, etc.')
    par = models.ManyToManyField('self', through='PAR', blank=True, verbose_name='part of', symmetrical=False,
                                 related_name='related_by_par',
                                 help_text='things of which this is a part of'
                                           '(a window is a part of a car, a house, a boat, etc.)')
    bga = models.ManyToManyField('self', through='BGA', blank=True, verbose_name='frequent followers', symmetrical=False,
                                 related_name='related_by_bga',
                                 help_text='words that frequently follow this '
                                           '(i.e. havoc follows wreak')
    bgb = models.ManyToManyField('self', through='BGB', blank=True, verbose_name='frequent predecessors', symmetrical=False,
                                 related_name='related_by_bgb',
                                 help_text='words that frequently precede this'
                                           '(i.e. wreck precedes havoc')
    rhy = models.ManyToManyField('self', through='RHY', blank=True, verbose_name='rhymes', symmetrical=False,
                                 help_text='perfect rhymes', related_name='related_by_rhy')
    nry = models.ManyToManyField('self', through='NRY', blank=True, verbose_name='near rhymes', symmetrical=False,
                                 help_text='approximate rhymes',
                                 related_name='related_by_nry')
    hom = models.ManyToManyField('self', through='HOM', blank=True, verbose_name='homophones', symmetrical=False,
                                 help_text='sound-alike words',
                                 related_name='related_by_hom')
    cns = models.ManyToManyField('self', through='CNS', blank=True, verbose_name='consonant matches', symmetrical=False,
                                 help_text='i.e. sample and simple',
                                 related_name='related_by_cns')

    class Meta:
        # for each language, there should be only one word with a certain name
        constraints = [models.UniqueConstraint(fields=['name', 'language'], name='unique_word_per_language'), ]

    def save(self, *args, **kwargs):
        self.name = self.name.lower()  # Convert name to lowercase
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        """String for representing the Model object"""
        return self.name


class WordRelation(models.Model):
    """Base class for classes that govern the ManyToManyFields that hold words related to a word."""

    # %(class)s is replaced with the lowercase of the class name in subclasses
    source_word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='%(class)s_relations')
    related_word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='linked_%(class)s_relations')

    # an integer returned by DataMuse that indicates relative popularity or relevance of the word compared to other
    # words in the list of related words
    score = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class JJA(WordRelation):
    pass


class JJB(WordRelation):
    pass


class SYN(WordRelation):
    pass


class TRG(WordRelation):
    pass


class ANT(WordRelation):
    pass


class SPC(WordRelation):
    pass


class GEN(WordRelation):
    pass


class COM(WordRelation):
    pass


class PAR(WordRelation):
    pass


class BGA(WordRelation):
    pass


class BGB(WordRelation):
    pass


class RHY(WordRelation):
    pass


class NRY(WordRelation):
    pass


class HOM(WordRelation):
    pass


class CNS(WordRelation):
    pass


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
    words = models.ManyToManyField(Word, through='Membership', related_name='words', related_query_name='word',
                                   blank=True)

    class Meta:
        # for each creator, there should only be one wordset with a given name
        constraints = [models.UniqueConstraint(fields=['name', 'creator'], name='unique_wordset_name_per_creator'), ]

    def get_absolute_url(self):
        """Returns the url to access a particular wordset instance."""
        return reverse('wordset-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object"""
        # if creator null, UniqueConstraint cannot be enforced; so identify wordset by name and id
        # todo instead of displaying id with anonymous creator, add an int to name based on how many other wordsets with this name exist?
        creator_string = f' ({self.id})'
        if self.creator is not None:
            creator_string = f' (created by {self.creator})'
        return f'{self.name}' + creator_string


class Membership(models.Model):
    """Class holding information for a word's inclusion in a wordset.

    Occurrences is the number of times the word appears in the set."""
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    wordset = models.ForeignKey(WordSet, on_delete=models.CASCADE)
    occurrences = models.IntegerField(default=1)

    class Meta:
        # for each WordSet and word, there should be only one Membership
        constraints = [models.UniqueConstraint(fields=['word', 'wordset'], name='unique_word_per_wordset'), ]

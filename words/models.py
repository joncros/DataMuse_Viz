from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models


class Word(models.Model):
    """Model representing a word and its relationships to other words."""
    name = models.CharField(max_length=100)
    parts_of_speech = models.ManyToManyField('PartOfSpeech', blank=True)

    # number of occurrences per million words of english text
    frequency = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)

    # JSON returned from DataMuse containing one or more strings defining the word
    definitions = JSONField(null=True, blank=True)

    # Remaining fields hold words related to this word.
    # Field names derived from three-letter codes used by rel_[code] DataMuse parameter
    jja = models.ManyToManyField('self', verbose_name='popular related noun', symmetrical=False,
                                 related_name='related_by_jja')
    jjb = models.ManyToManyField('self', verbose_name='popular related adjective', symmetrical=False,
                                 related_name='related_by_jjb')
    syn = models.ManyToManyField('self', verbose_name='synonym', related_name='synonyms',
                                 related_query_name='synonym')

    # Words that are statistically associated with this word in the same piece of text
    trg = models.ManyToManyField('self', verbose_name='triggers', symmetrical=False,
                                 related_name='words_is_trigger_for', related_query_name='is_trigger_for')

    ant = models.ManyToManyField('self', verbose_name='antonyms', related_name='antonyms',
                                 related_query_name='antonym')
    spc = models.ManyToManyField('self', verbose_name='direct hypernyms', symmetrical=False,
                                 help_text='words with a similar, but broader meaning '
                                           '(i.e. boat is a hypernym of gondola)',
                                 related_name='hyponyms', related_query_name='hyponym')
    gen = models.ManyToManyField('self', verbose_name='direct hyponyms', symmetrical=False,
                                 help_text='words with a similar, but more specific meaning '
                                           '(i.e. gondola is a hyponym of boat)',
                                 related_name='hypernyms', related_query_name='hypernym')
    com = models.ManyToManyField('self', verbose_name='comprises', symmetrical=False,
                                 help_text='things which this is composed of'
                                           '(a car has an accelerator, a steering wheel, etc.',
                                 related_name='part_of')
    par = models.ManyToManyField('self', verbose_name='part of', symmetrical=False,
                                 help_text='things of which this is a part of'
                                           '(a window is a part of a car, a house, a boat, etc.)',
                                 related_name='comprises')
    bga = models.ManyToManyField('self', verbose_name='frequent followers', symmetrical=False,
                                 help_text='words that frequently follow this '
                                           '(i.e. wreak followed by havoc',
                                 related_name='frequently_follows')
    bgb = models.ManyToManyField('self', verbose_name='frequent predecessors', symmetrical=False,
                                 help_text='words that frequently precede this'
                                           '(i.e. havoc preceding wreak',
                                 related_name='frequently_precedes')
    rhy = models.ManyToManyField('self', verbose_name='rhymes', help_text='perfect rhymes',
                                 related_name='rhymes', related_query_name='rhyme')
    nry = models.ManyToManyField('self', verbose_name='near rhymes', help_text='approximate rhymes',
                                 related_name='near_rhymes', related_query_name='near_rhyme')
    hom = models.ManyToManyField('self', verbose_name='homophones', help_text='sound-alike words',
                                 related_name='homophones', related_query_name='homophone')
    cns = models.ManyToManyField('self', verbose_name='consonant matches', help_text='i.e. sample and simple',
                                 related_name='consonant_matches', related_query_name='consonant_match')
    # todo review which many-to-many fields should be asymmetrical
    # todo add rel_name and rel_query_name if/where appropriate for asymmetrical fields

    def __str__(self):
        """String for representing the Model object"""
        return self.name


class Language(models.Model):
    """Model representing a language supported by DataMuse (currently, English or Spanish"""

    # tuple holding available language choices. first item in each nested tuple is the ISO 639-1 code
    name_choices = (
        ('en', 'English'),
        ('es', 'Spanish'),
    )

    name = models.CharField(
        max_length=2,
        choices=name_choices,
        blank=False,
        default='en',
        help_text='Language',
    )

    def __str__(self):
        """String for representing the Model object"""
        return self.get_name_display()

    # todo method (may not belong in models) to add "v=name", if name not en, to DataMuse queries
    # todo setting or property somewhere to indicate DataMuse parameters not supported by a language
    # todo confirm what is returned by __str__()


class PartOfSpeech(models.Model):
    """Model representing a part of speech (noun, verb, adjective, adverb or unknown."""

    # tuple uses abbreviations used by DataMuse
    part_choices = (
        ('n', 'noun'),
        ('v', 'verb'),
        ('adj', 'adjective'),
        ('adv', 'adverb'),
        # ('u', 'unknown'),  blank value will indicate unknown instead of 'u'
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

    # todo confirm what is returned by __str__()



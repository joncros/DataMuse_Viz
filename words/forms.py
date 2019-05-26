import logging

from django import forms
from django.forms import Textarea
from django.utils.translation import ugettext_lazy as _

from words.models import Word, WordSet

# Get an instance of a logger
logger = logging.getLogger(__name__)

# tuple holding word relationship types
relations = (
    ('jja', Word._meta.get_field('jja').verbose_name),
    ('jjb', Word._meta.get_field('jjb').verbose_name),
    ('syn', Word._meta.get_field('syn').verbose_name),
    ('trg', Word._meta.get_field('trg').verbose_name),
    ('ant', Word._meta.get_field('ant').verbose_name),
    ('spc', Word._meta.get_field('spc').verbose_name),
    ('gen', Word._meta.get_field('gen').verbose_name),
    ('com', Word._meta.get_field('com').verbose_name),
    ('par', Word._meta.get_field('par').verbose_name),
    ('bga', Word._meta.get_field('bga').verbose_name),
    ('bgb', Word._meta.get_field('bgb').verbose_name),
    ('rhy', Word._meta.get_field('rhy').verbose_name),
    ('nry', Word._meta.get_field('nry').verbose_name),
    ('hom', Word._meta.get_field('hom').verbose_name),
    ('cns', Word._meta.get_field('cns').verbose_name),
)


class WordCharField(forms.CharField):
    """Custom CharField that treats each line from the Widget as a separate string and returns a list"""

    widget = Textarea

    def to_python(self, value):
        if not value:
            return []
        else:
            # an HTML line break in an input fields is CR LF
            return value.split('\r\n')


class WordSetCreateForm(forms.ModelForm):
    """Form to create a WordSet"""

    # Field allows user to type one word or phrase (to be added to the new WordSet) per line in the Textarea
    words = WordCharField(strip=False, help_text="Type the words to include in the set (one word or phrase per line)")

    class Meta:
        model = WordSet
        fields = ['name', 'description', 'creator']

        # hide creator field; field needed so validation occurs for model 'unique_wordset_name_per_creator' constraint
        widgets = {'creator': forms.HiddenInput()}

    def save(self, commit=True):
        # todo run DataMuse query for each word from words field

        logger.debug('WordSetCreateForm save')

        # do initial save of new wordset
        instance = super(WordSetCreateForm, self).save(commit=commit)

        # get or create Words from 'words' field, add to instance field "words"
        for word in self.cleaned_data['words']:
            logger.debug(f'word from Textarea: {word}')
            # instance is the first item in the tuple returned by get_or_create
            word_instance = Word.objects.get_or_create(name=word)[0]
            self.instance.words.add(word_instance)

        if commit:
            instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        # get current user
        self.user = kwargs.pop('user', None)
        super(WordSetCreateForm, self).__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            logger.debug(f'self.user: {self.user}')
            self.fields['creator'].initial = self.user  # set creator to current user
        else:
            # no authenticated user, set creator field to blank
            logger.debug("self.user is AnonymousUser or None")
            self.fields['creator'].initial = ''


class WordForm(forms.ModelForm):
    """Form to input a word and send a DataMuse Query"""
    relation = forms.ChoiceField(choices=relations)
    # todo (in views?) use relation choice to display correct visualization. pass relation to context?

    # word_sets = WordSet.objects().filter(creator__exact=None)
    # word_sets += WordSet.objects().filter(creator__exact=self.user)
    word_set = forms.ModelChoiceField(queryset=WordSet.objects.all(), widget=forms.Select, required=False)
    #word_set = forms.ModelChoiceField(queryset=WordSet.objects.filter(creator=None),
                                      #widget=forms.Select, required=False)

    class Meta:
        model = Word
        fields = ['name', 'language', ]
        labels = {'name': _('Word')}

        # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user', None)
    #     super(WordForm, self).__init__(*args, **kwargs)
    #     # if I only wanted to show WordSets created by current user:
    #     if self.user.is_authenticated:
    #         #if WordSet:
    #             #self.fields['word_set'] = WordSet.objects.filter(creator=self.user)
    #         pass



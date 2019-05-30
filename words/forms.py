import logging
import reimport magic
from django import forms
from django.core.exceptions import ValidationErrorfrom django.forms import Textarea
from django.utils.translation import ugettext_lazy as _
from string import punctuation
from words import datamuse_jsonfrom words.models import Word, WordSet

# Get an instance of a logger
logger = logging.getLogger(__name__)

# tuple holding word relationship codes and their verbose namesrelations = tuple(    (relation_code, Word._meta.get_field(relation_code).verbose_name) for relation_code in datamuse_json.relation_codes)

class WordCharField(forms.CharField):
    """Custom CharField that treats each line from the Widget as a separate string and returns a list"""

    widget = Textarea

    def to_python(self, value):
        if not value:
            return []
        else:
            # an HTML line break in an input fields is CR LF
            # todo split punctuation from beginning and end of each word? at least strip " and '            return value.split('\r\n')


class WordFileField(forms.FileField):    """File field that accepts text files and splits the text at whitespace, returning an array of strings    Detects and removes punctuation so that, for example, prose works can be uploaded to form a set of words."""    def to_python(self, data):        result = []        if data:            # confirm that file is plain text, raise error if it is not            m = magic.Magic(magic_file=r"words\static\magic.mgc", mime=True)            file_type = m.from_buffer(data.read())            if file_type != "text/plain":                raise ValidationError("Uploaded file is not a plain text file.")            # string to match either '--' or any whitespace surrounded by zero or more punctuation characters            pattern_string = "[" + re.escape(punctuation) + "]*" "\\-\\-" "[" + re.escape(punctuation) + "]*" \                             "|" \                             "[" + re.escape(punctuation) + "]*" "\\s" "[" + re.escape(punctuation) + "]*"            # regex pattern for above string            pattern = re.compile(pattern_string)            for chunk in data.chunks():                # split file into individual words, discarding whitespace and punctuation at either end of a word                array = pattern.split(chunk.decode())                # add items in array to result                result.extend(array)            # remove any punctuation from the end of the last item in result            pattern = "[" + re.escape(punctuation) + "]*\\Z"            result[-1] = re.sub(pattern, '', result[-1])        return resultclass WordSetCreateForm(forms.ModelForm):
    """Form to create a WordSet"""

    # Field allows user to type one word or phrase (to be added to the new WordSet) per line in the Textarea
    words = WordCharField(strip=False, required=False,                          help_text="(Optional) Type the words to include in the set (one word or phrase per line)")
    # Field allows user to upload a text file containing words to include in the set    text_file = WordFileField(required=False,                                   help_text="(Optional) Upload a text file containing words (multiple words per line) "                                             "to include in the set. The text is split into individual words (no "                                             "phrases will be detected).")    class Meta:
        model = WordSet
        fields = ['name', 'description', 'creator']

        # hide creator field; field needed so validation occurs for model 'unique_wordset_name_per_creator' constraint
        widgets = {'creator': forms.HiddenInput()}

    def save(self, commit=True):
        logger.debug('WordSetCreateForm save')

        # do initial save of new wordset
        instance = super(WordSetCreateForm, self).save(commit=commit)

        # get or create Words from 'words' field, add to instance field "words"
        for word in self.cleaned_data['words']:
            logger.debug(f'word from Textarea: {word}')
            word_instance = datamuse_json.add_or_update_word(word)            self.instance.words.add(word_instance)

        # get or create Words from uploaded text file        for word in self.cleaned_data['text_file']:            word_instance = datamuse_json.add_or_update_word(word)            self.instance.words.add(word_instance)        if commit:
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

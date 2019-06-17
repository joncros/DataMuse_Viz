import loggingimport reimport magicfrom django import formsfrom django.core.exceptions import ValidationErrorfrom django.forms import Textareafrom django.utils.translation import ugettext_lazy as _from string import punctuationfrom words import datamuse_jsonfrom words.models import Word, WordSet# Get an instance of a loggerlogger = logging.getLogger(__name__)# tuple holding word relationship codes and their verbose namesrelations = tuple(    (relation_code, Word._meta.get_field(relation_code).verbose_name) for relation_code in datamuse_json.relation_codes)class WordCharField(forms.CharField):    """Custom CharField that treats each line from the Widget as a separate string and returns a list"""    widget = Textarea    def to_python(self, value):        if not value:            return []        else:            # an HTML line break in an input fields is CR LF            # todo allow phrases surrounded by ""            return value.split('\r\n')class WordFileField(forms.FileField):    """File field that accepts text files and splits the text at whitespace, returning an array of strings    Detects and removes punctuation so that, for example, prose works can be uploaded to form a set of words."""    def to_python(self, data):        result = []        if data:            # confirm that file is plain text, raise error if it is not            m = magic.Magic(magic_file=r"words\static\magic.mgc", mime=True)            file_type = m.from_buffer(data.read())            if file_type != "text/plain":                raise ValidationError("Uploaded file is not a plain text file.")            # punctuation characters (excluding -) escaped for regular expressions            p = re.escape(punctuation[:12] + punctuation[13:])            # string for splitting data into words. splits input at:            #   one or more characters that are whitespace or punctuation (excluding the - character)            #   or the em-dash, '--', and any surrounding non-word characters            #   or the dash -, only when it is surrounded by non-word characters, so that hyphenated words are not split            pattern_string = f'[{p}\s]+' \                '|' '\W*\\-\\-\W*' \                '|' '(?<=\W)\\-(?=\W)'            # regex pattern from above string            pattern = re.compile(pattern_string)            for chunk in data.chunks():                # split file into individual words                array = pattern.split(chunk.decode())                # remove items which are an empty string from array                array = list(filter(None, array))                # add items in array to result                result.extend(array)        return resultclass WordSetCreateForm(forms.ModelForm):    """Form to create a WordSet"""    # Field allows user to type one word or phrase (to be added to the new WordSet) per line in the Textarea    words = WordCharField(strip=False, required=False,                          help_text="(Optional) Type the words to include in the set (one word or phrase per line)")    # Field allows user to upload a text file containing words to include in the set    text_file = WordFileField(required=False,                              help_text="(Optional) Upload a text file containing words (multiple words per line) "                                        "to include in the set. The text is split into individual words (no "                                        "phrases will be detected).")    class Meta:        model = WordSet        fields = ['name', 'description', 'creator']        # hide creator field; field needed so validation occurs for model 'unique_wordset_name_per_creator' constraint        widgets = {'creator': forms.HiddenInput()}    def save(self, commit=True):        logger.debug('WordSetCreateForm save')        # do initial save of new wordset        instance = super(WordSetCreateForm, self).save(commit=commit)        # get words and occurrences from 'words' field        detected_words = dict()  # dict to hold words and the number of occurrences of each word        for word in self.cleaned_data['words']:            logger.debug(f'word from Textarea: {word}')            if word not in detected_words:                detected_words[word] = 1            else:                detected_words[word] += 1        # get words and occurrences from uploaded text file        for word in self.cleaned_data['text_file']:            if word not in detected_words:                detected_words[word] = 1            else:                detected_words[word] += 1        # get or create each word instance and add to WordSet with the number of occurrences        for word, count in detected_words.items():            word_instance = datamuse_json.add_or_update_word(word)            if word_instance:  # word is a valid word according to DataMuse                self.instance.words.add(word_instance, through_defaults={'occurrences': count})        if commit:            instance.save()        return instance    def __init__(self, *args, **kwargs):        # get current user        self.user = kwargs.pop('user', None)        super(WordSetCreateForm, self).__init__(*args, **kwargs)        if self.user and self.user.is_authenticated:            logger.debug(f'self.user: {self.user}')            self.fields['creator'].initial = self.user  # set creator to current user        else:            # no authenticated user, set creator field to blank            logger.debug("self.user is AnonymousUser or None")            self.fields['creator'].initial = ''class RelatedWordsForm(forms.Form):    """Form to input a word and send a DataMuse Query"""    word = forms.CharField()    relations = forms.MultipleChoiceField(        choices=relations,        widget=forms.CheckboxSelectMultiple()    )    # hidden field to pass DataMuse results to view    results = forms.CharField(widget=forms.HiddenInput, required=False)    def clean(self):        super().clean()        try:            logger.debug(f"cleaned data: {self.cleaned_data}")            if 'relations' not in self.cleaned_data:                raise ValidationError('Please check at least one relation.')            chosen_relations = self.cleaned_data['relations']            results = {                relation: datamuse_json.add_related(self.cleaned_data['word'], relation)[1]                for relation in chosen_relations            }            logger.debug(f'results {results}')            self.cleaned_data['word'] = Word.objects.get(name=self.cleaned_data['word'])            self.cleaned_data['results'] = results            logger.debug(f"new cleaned data: {self.cleaned_data}")        except ConnectionError as e:            raise ValidationError(e)        except ValueError as e:            message = "Invalid parameter for DataMuse query: " + str(e)            raise ValidationError(message)        return self.cleaned_dataclass WordSetChoice(forms.Form):    """Form to select a WordSet out of the existing WordSets."""    word_set = forms.ModelChoiceField(queryset=WordSet.objects.all(), widget=forms.Select)    frequency_gt = forms.DecimalField(widget=forms.TextInput(attrs={'size': 6}), required=False,                                      label="Only show words with frequency greater than")    frequency_lt = forms.DecimalField(widget=forms.TextInput(attrs={'size': 6}), required=False,                                      label="Only show words with frequency less than")    def clean(self):        cleaned_data = super().clean()        frequency_gt = cleaned_data.get("frequency_gt")        frequency_lt = cleaned_data.get("frequency_lt")        if frequency_gt and frequency_lt:            # Only do something if both fields are valid so far.            if frequency_gt > frequency_lt:                raise forms.ValidationError(                    "frequency less than field must be greater than frequency greater than field")
import loggingimport refrom time import process_time_nsfrom typing import Listimport magicfrom crispy_forms.helper import FormHelperfrom crispy_forms.layout import Layout, Row, Column, Div, Submit, Fieldfrom django import formsfrom django.core.exceptions import ValidationErrorfrom django.forms import Textareafrom string import punctuationfrom words import datamuse_jsonfrom words.datamuse_json import DatamuseWordNotRecognizedErrorfrom words.models import Word, WordSet# Get an instance of a loggerlogger = logging.getLogger(__name__)# tuple holding word relationship codes and their verbose namesrelations = tuple(    (relation_code, Word._meta.get_field(relation_code).verbose_name) for relation_code in datamuse_json.relation_codes)class WordCharField(forms.CharField):    """Custom CharField that treats each line from the Widget as a separate string and returns a list"""    widget = Textarea    def to_python(self, value):        if not value:            return []        else:            # an HTML line break in an input fields is CR LF            # todo allow phrases surrounded by ""            return value.split('\r\n')class WordFileField(forms.FileField):    """File field that accepts text files and splits the text at whitespace, returning an array of strings    Detects and removes punctuation so that, for example, prose works can be uploaded to form a set of words."""    def to_python(self, data):        start = process_time_ns()        result = []        if data:            # only accept files of 10 mb or less            if data.size > 10000000:                raise ValidationError("Uploaded file is to large; file size cannot exceed 10 mb.")            # confirm that file is plain text, raise error if it is not            file_type = magic.from_buffer(data.read(), mime=True)            if file_type != "text/plain":                raise ValidationError("Uploaded file is not a plain text file.")            # punctuation characters (excluding -) escaped for regular expressions            p = re.escape(punctuation[:12] + punctuation[13:])            # string for splitting data into words. splits input at:            #   one or more characters that are whitespace or punctuation (excluding the - character)            #   or the em-dash, '--', and any surrounding non-word characters            #   or the dash -, only when it is surrounded by non-word characters, so that hyphenated words are not split            pattern_string = f'[{p}\s]+' \                             '|' '\W*\\-\\-\W*' \                             '|' '(?<=\W)\\-(?=\W)'            # regex pattern from above string            pattern = re.compile(pattern_string)            for line in data:                # decode text using utf8. error handler "backslashreplace" replaces unrecognized characters with the                # equivalent numeric escape sequence rather than throwing UnicodeDecodeError like the default error                # handler would.                array = pattern.split(line.decode(errors='backslashreplace'))                array = list(filter(None, array))                result.extend(array)            end = process_time_ns()            logger.debug(f'result size: {len(result)}, ns elapsed: {end - start}')        return resultdef wordset_form_process(wordset: WordSet, commit=True, *args: List[str]):    """Helper for WordSetCreateForm save method. Adds words from the form to the new WordSet.    Arguments: wordset, a WordSet; args, one or more lists of strings. Adds a Word corresponding to each string in    the list(s) to the WordSet and sets the occurrences (in the Membership shared by the WordSet and the Word) to the    number of times the string occurs across all of the lists."""    detected_words = dict()    # get words and occurrences from each list    for word_list in args:        for word in word_list:            if word not in detected_words:                detected_words[word] = 1            else:                detected_words[word] += 1    # get or create each word instance and add to WordSet with the number of occurrences    for word, count in detected_words.items():        word_instance = datamuse_json.add_or_update_word(word)        if word_instance:  # word is a valid word according to DataMuse            wordset.words.add(word_instance, through_defaults={'occurrences': count})        else:            # add the word followed by a line break to unrecognized_words field, so that each unrecognized word appears            # on its own line when the field is displayed to the user.            wordset.unrecognized_words = wordset.unrecognized_words + f'{word}<br>'    if commit:        wordset.save()    return wordsetclass WordSetCreateForm(forms.ModelForm):    """Form to create a WordSet"""    # Field allows user to type one word or phrase (to be added to the new WordSet) per line in the Textarea    words = WordCharField(strip=False, required=False,                          help_text="(Optional) Type the words to include in the set (one word or phrase per line)")    # Field allows user to upload a text file containing words to include in the set    text_file = WordFileField(required=False,                              help_text="(Optional) Upload a text file containing words (multiple words per line) "                                        "to include in the set. The text is split into individual words (no "                                        "phrases will be detected). Punctuation (apart from hyphens) will be ignored.")    class Meta:        model = WordSet        fields = ['name', 'description', 'creator']        widgets = {            # hide creator field; field needed so validation occurs for 'unique_wordset_name_per_creator' constraint            'creator': forms.HiddenInput(),        }    def save(self, commit=True):        logger.debug('WordSetCreateForm save')        # do initial save of new wordset        instance = super(WordSetCreateForm, self).save(commit=commit)        # process words from form fields        wordset_form_process(instance, commit, self.cleaned_data['words'], self.cleaned_data['text_file'])        return instance    def __init__(self, *args, **kwargs):        # get current user        self.user = kwargs.pop('user', None)        super(WordSetCreateForm, self).__init__(*args, **kwargs)        if self.user and self.user.is_authenticated:            logger.debug(f'self.user: {self.user}')            self.fields['creator'].initial = self.user  # set creator to current user        else:            # no authenticated user, set creator field to blank            logger.debug("self.user is AnonymousUser or None")            self.fields['creator'].initial = ''        # control rendering using django-crispy-forms        self.helper = FormHelper()        self.helper.layout = Layout(            Row(                Column('name', css_class='form-group col-md-4'),            ),            Row(                Column('description', css_class='form-group col-md-6'),            ),            Row(                Column('words', css_class='form-group col-md-6'),            ),            'text_file',        )def related_words_query(word: str, relation_codes: List[str]):    """Helper for RelatedWordsForm. relation_codes is a list of strings corresponding to the desired relation types.    Returns a dictionary where each key is the relationship code and the value is the model field holding the words    related to the word.    Valid strings for relation_codes are in datamuse_json.relation_codes."""    result = {}    for code in relation_codes:        # retrieve the Words related to word for that relationship type        query_result = datamuse_json.add_related(word, code)[1]        if query_result.count() > 0:            # add item to dict with key corresponding to relation            result[code] = query_result    return resultclass RelatedWordsForm(forms.Form):    """Form to input a word and send a DataMuse Query"""    word = forms.CharField()    relations = forms.MultipleChoiceField(        choices=relations,        widget=forms.CheckboxSelectMultiple()    )    # hidden field to pass DataMuse results to view    results = forms.CharField(widget=forms.HiddenInput, required=False)    def clean(self):        super().clean()        try:            logger.debug(f"cleaned data: {self.cleaned_data}")            if 'relations' not in self.cleaned_data:                raise ValidationError('Please check at least one relation.')            results = related_words_query(self.cleaned_data['word'], self.cleaned_data['relations'])            logger.debug(f'results {results}')            if not results:                # query returned empty results for all of the relations                raise ValidationError(                    'No related words found for word "%(word)s" for the chosen relations',                    params={'word': self.cleaned_data['word']},                )            self.cleaned_data['word'] = Word.objects.get(name=self.cleaned_data['word'])            self.cleaned_data['results'] = results            logger.debug(f"new cleaned data: {self.cleaned_data}")        except ConnectionError as e:            raise ValidationError(e)        except ValueError as e:            message = "Invalid parameter for Datamuse query: " + str(e)            raise ValidationError(message)        except DatamuseWordNotRecognizedError as e:            raise ValidationError(e.message)        return self.cleaned_dataclass WordSetChoice(forms.Form):    """Form to select a WordSet out of the existing WordSets."""    word_set = forms.ModelChoiceField(queryset=WordSet.objects.all(), widget=forms.Select)    frequency_gt = forms.DecimalField(widget=forms.TextInput(attrs={'size': 6}), required=False,                                      label="Only show words with frequency greater than")    frequency_lt = forms.DecimalField(widget=forms.TextInput(attrs={'size': 6}), required=False,                                      label="Only show words with frequency less than")    def clean(self):        cleaned_data = super().clean()        frequency_gt = cleaned_data.get("frequency_gt")        frequency_lt = cleaned_data.get("frequency_lt")        if frequency_gt and frequency_lt:            # Only do something if both fields are valid so far.            if frequency_gt > frequency_lt:                raise forms.ValidationError(                    "frequency less than field must be greater than frequency greater than field")class ScatterplotWordSetChoice(WordSetChoice):    """Adds fields for limiting the displayed words by an upper or lower limit on word occurrences."""    occurrences_gt = forms.IntegerField(widget=forms.TextInput(attrs={'size': 6}), required=False,                                        label="Only show words with occurrences greater than")    occurrences_lt = forms.IntegerField(widget=forms.TextInput(attrs={'size': 6}), required=False,                                        label="Only show words with occurrences less than")    def __init__(self, *args, **kwargs):        super(ScatterplotWordSetChoice, self).__init__(*args, **kwargs)        # control rendering using django-crispy-forms        self.helper = FormHelper()        self.helper.form_class = 'form-horizontal'        self.helper.form_method = 'post'        self.helper.add_input(Submit('submit', 'Submit', css_class='button'))        self.helper.layout = Layout(            Div(                Div('word_set', css_class='col-lg-12 col-md-12 col-sm-12 col-xs-12'),                css_class='form-group'            ),            Div(                Div('frequency_gt', css_class='col-lg-5 col-md-5'),                Div('frequency_lt', css_class='col-lg-5 col-md-5'),                css_class='form-group'            ),            Div(                Div('occurrences_gt', css_class='col-lg-5 col-md-5'),                Div('occurrences_lt', css_class='col-lg-5 col-md-5'),                css_class='form-group'            ),        )    def clean(self):        super().clean()        occurrences_gt = self.cleaned_data.get("occurrences_gt")        occurrences_lt = self.cleaned_data.get("occurrences_lt")        if occurrences_gt and occurrences_lt:            # Only do something if both fields are valid so far.            if occurrences_gt > occurrences_lt:                raise forms.ValidationError(                    "occurrences less than field must be greater than occurrences greater than field")
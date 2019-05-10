from django import forms

from words.models import Word, WordSet

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


class WordSetForm(forms.ModelForm):
    """Form to create a WordSet"""

    class Meta:
        model = WordSet
        fields = ['name', 'description', ]

    def __init__(self, *args, **kwargs):
        # get current user
        self.user = kwargs.pop('user', None)
        super(WordSetForm, self).__init__(*args, **kwargs)


class WordForm(forms.ModelForm):
    """Form to input a word and send a DataMuse Query"""
    relation = forms.ChoiceField(choices=relations)
    # word_sets = WordSet.objects().filter(creator__exact=None)
    # word_sets += WordSet.objects().filter(creator__exact=self.user)
    word_set = forms.ModelChoiceField(queryset=WordSet.objects.all(), widget=forms.Select, required=False)
    #word_set = forms.ModelChoiceField(queryset=WordSet.objects.filter(creator=None),
                                      #widget=forms.Select, required=False)

    class Meta:
        model = Word
        fields = ['name', 'language', ]

    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user', None)
    #     super(WordForm, self).__init__(*args, **kwargs)
    #     # if I only wanted to show WordSets created by current user:
    #     if self.user.is_authenticated:
    #         #if WordSet:
    #             #self.fields['word_set'] = WordSet.objects.filter(creator=self.user)
    #         pass



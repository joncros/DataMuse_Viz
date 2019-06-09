import json
import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import UserPassesTestMixin, AccessMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from words import datamuse_json
from words.forms import RelatedWordsForm, WordSetCreateForm, WordSetChoice
from words.models import WordSet

# Get an instance of a logger
logger = logging.getLogger(__name__)


def index(request):
    """View function for home tab of site."""
    context = {
        "navbar_index": "active"  # make "Home" the active item in the navbar
    }

    return render(request, 'words/index.html', context)


def visualization_frequency(request):
    """View for displaying a bubble chart of the frequencies of words in a WordSet"""

    context = {
        'viz_title': 'Word Frequencies',  # Visualization title to use in page title
        'navbar_visualization_frequency': 'active',  # make "Word Frequencies Visualization" active in the navbar
    }

    if request.method == 'POST':
        form = WordSetChoice(request.POST)

        if form.is_valid():
            set_instance = form.cleaned_data['word_set']
            logger.debug(set_instance.name)
            queryset = set_instance.words.all()

            # apply limits on word frequency (if any)
            if form.cleaned_data['frequency_gt']:
                queryset = queryset.filter(frequency__gt=form.cleaned_data['frequency_gt'])
            if form.cleaned_data['frequency_lt']:
                queryset = set_instance.words.filter(frequency__lt=form.cleaned_data['frequency_lt'])

            json_list = [
                {
                    "name": word.name,
                    "title": f'{word.name}',
                    "group": set_instance.name,
                    "value": word.frequency
                }
                for word in queryset]
            context['wordcount'] = len(json_list)  # number of words in visualization

            # json formatted for Observable bubble chart
            wordset_data = json.dumps(json_list, cls=DjangoJSONEncoder)
            context['wordset_data'] = wordset_data
    else:
        form = WordSetChoice()

    context['form'] = form

    return render(request, 'words/visualization_frequency.html', context)


def visualization_related_words(request):
    """View for the word relationship visualization"""
    # todo refactor into class-based visualization view that I can subclass?

    # todo add visualization description string to context

    context = {
        'viz_title': 'Related Words',  # Visualization title to use in page title
        'navbar_related_words': 'active',  # make "Word Relationships Visualization" the active item in the navbar
    }

    if request.method == 'POST':
        # create form instances and populate them with data from the request:
        related_words_form = RelatedWordsForm(request.POST)

        if related_words_form.is_valid():
            instance = related_words_form.cleaned_data['word']
            code = related_words_form.cleaned_data['relation']
            logger.debug(f"instance: {instance}, code: {code}")
            word_attr = getattr(instance, code)
            related_words = word_attr.all()
            logger.debug(f'related_words: {related_words}')

            # object holding the data in the format needed by the D3 Observable chart
            json_object = {
                "name": instance.name,
                "children": [
                    {"name": word.name}
                    for word in related_words]
            }
            data = json.dumps(json_object)
            context['data'] = data

    # if a GET (or any other method) create a blank form
    else:
        related_words_form = RelatedWordsForm()

    # always add form to context
    context['related_words_form'] = related_words_form

    return render(request, 'words/visualization_related_words.html', context)


# todo view for page visualizing the frequency (google nwords) of words in a set (bubble chart)


# todo? view for page visualizing # of occurrences of words in a set of words vs nwords frequency of the words


class WordSetDetailView(generic.DetailView):
    model = WordSet


class WordSetCreate(CreateView):
    """View to create a new WordSet"""
    model = WordSet
    form_class = WordSetCreateForm

    def get_form_kwargs(self):
        """Add request user to form kwargs"""
        kwargs = super(WordSetCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(WordSetCreate, self).get_context_data()
        context['navbar_wordset_create'] = 'active'
        return context

    def get_success_url(self):
        """Return the URL to redirect to. If request has next parameter, redirect there"""
        next_url = self.request.GET.get('next', None)
        logger.debug(f'next_url: {next_url}')
        if next_url:
            return str(next_url)
        else:
            # Redirect to wordset-detail page for new instance
            return self.object.get_absolute_url()


class WordSetDelete(UserPassesTestMixin, DeleteView):
    model = WordSet
    success_url = reverse_lazy('index')

    # Deny access if WordSet creator is not signed in
    def test_func(self):
        creator = self.get_object().creator
        return self.request.user == creator

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().creator is None:
            # If WordSet instance has no creator, respond with 403 error even if user not logged in
            self.raise_exception = True
        return super(WordSetDelete, self).dispatch(request, *args, **kwargs)


class WordSetListView(generic.ListView):
    model = WordSet

    # todo add word count to template?

    def get_context_data(self, *args, **kwargs):
        context = super(WordSetListView, self).get_context_data()
        context['navbar_wordsets'] = 'active'
        return context


# views providing json data required by visualizations


def word_frequencies_for_wordset(request):
    """Returns json holding the words from a wordset and their frequency, for use by the word frequency bubble chart.

    In the future, words may be grouped by their part of speech. This would determine the color of the bubble for each word.
    Returns an array of json objects. The chart requires object to have a name, title, group and value. Here,
    the name is the word, the title is word([parts of speech]), the group is the same for all words and the value is the
     word frequency."""

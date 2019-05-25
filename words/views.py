import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from words.forms import WordForm, WordSetCreateForm
from words.models import WordSet

# Get an instance of a logger
logger = logging.getLogger(__name__)


def index(request):
    """View function for home tab of site."""
    context = {
        "navbar_index": "active"   # make "Home" the active item in the navbar
               }

    return render(request, 'words/index.html', context)


def get_relation_viz(request):
    """View for the word relationship visualization"""
    # todo refactor into class-based visualization view that I can subclass?

    # todo add visualization description string to context

    if request.method == 'POST':
        # create form instances and populate them with data from the request:
        word_form = WordForm(request.POST)

    # if a GET (or any other method) create a blank form
    else:
        word_form = WordForm()

    context = {
        'viz_title': 'Word Relationships',  # Visualization title to use in page title
        'navbar_relation_viz': 'active',  # make "Word Relationships Visualization" the active item in the navbar
        'word_form': word_form,
    }

    return render(request, 'words/word_relationships.html', context)


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


class WordSetDelete(DeleteView):
    model = WordSet
    success_url = reverse_lazy('index')


class WordSetListView(generic.ListView):
    model = WordSet

    def get_context_data(self, **kwargs):
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
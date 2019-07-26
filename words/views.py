import decimal
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
from words.models import WordSet, Word

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
                queryset = queryset.filter(frequency__lt=form.cleaned_data['frequency_lt'])

            # objects to pass to D3
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

    # if a GET (or any other method) create a blank form
    else:
        # id parameter in url, when present indicates the WordSet that should be initially selected in the form
        wordset_id = request.GET.get('id', None)
        logger.debug(f'id from url: {wordset_id}')

        if wordset_id:
            try:
                wordset = WordSet.objects.get(id=wordset_id)
                logger.debug(f'Initial WordSet from url: {wordset}')
                form = WordSetChoice(initial={'word_set': wordset})
            except WordSet.DoesNotExist:
                logger.info(
                    f'WordSet id {wordset_id} passed to frequency visualization, but no WordSet '
                    f'with this id exists.')
                form = WordSetChoice()
        else:
            form = WordSetChoice()

    # always add form to context
    context['form'] = form

    return render(request, 'words/visualization_frequency.html', context)


def visualization_frequency_scatterplot(request):
    """View for a chart that plots frequency of words vs their number of occurrences in a WordSet."""
    context = {
        'viz_title': 'Occurrences vs Frequencies Scatterplot',  # Visualization title to use in page title
        'navbar_frequency_scatterplot': 'active',  # make this page the active item in the navbar
    }

    if request.method == 'POST':
        form = WordSetChoice(request.POST)

        if form.is_valid():
            set_instance = form.cleaned_data['word_set']
            logger.debug(set_instance.name)

            # get the Membership objects (each holds the word and occurrences in the WordWet) linked to the WordSet
            queryset = set_instance.membership_set.all()

            # apply limits on word frequency (if any)
            if form.cleaned_data['frequency_gt']:
                queryset = queryset.filter(word__frequency__gt=form.cleaned_data['frequency_gt'])
            if form.cleaned_data['frequency_lt']:
                queryset = queryset.filter(word__frequency__lt=form.cleaned_data['frequency_lt'])

            logger.debug(queryset)

            # objects to pass to D3
            data_list = [
                {
                    "name": membership.word.name,
                    "x": membership.occurrences,
                    "y": membership.word.frequency
                }
                for membership in queryset]

            logger.debug(f'data_list: {data_list}')

            # format data_list as json string
            word_data = json.dumps(data_list, cls=DjangoJSONEncoder)
            context['word_data'] = word_data

    # if a GET (or any other method) create a blank form
    else:
        # id parameter in url, when present indicates the WordSet that should be initially selected in the form
        wordset_id = request.GET.get('id', None)
        logger.debug(f'id from url: {wordset_id}')

        if wordset_id:
            try:
                wordset = WordSet.objects.get(id=wordset_id)
                logger.debug(f'Initial WordSet from url: {wordset_id} {wordset}')
                form = WordSetChoice(initial={'word_set': wordset})
            except WordSet.DoesNotExist:
                logger.info(f'WordSet id {wordset_id} passed to frequency visualization scatterplot, but no WordSet '
                            f'with this id exists.')
                form = WordSetChoice()
        else:
            form = WordSetChoice()

    # always add form to context
    context['form'] = form
    logger.debug(context)

    return render(request, 'words/visualization_frequency_scatterplot.html', context)


def visualization_related_words(request):
    """View for the word relationship visualization"""

    context = {
        'viz_title': 'Related Words',  # Visualization title to use in page title
        'navbar_related_words': 'active',  # make "Word Relationships Visualization" the active item in the navbar
    }

    if request.method == 'POST':
        # create form instances and populate them with data from the request
        form = RelatedWordsForm(request.POST)

        if form.is_valid():
            instance = form.cleaned_data['word']
            codes = form.cleaned_data['relations']
            results = form.cleaned_data['results']
            logger.debug(f"instance: {instance}, code: {codes}")

            result_dict = {
                "name": instance.name,
                "children": [
                    {
                        "name":
                            Word._meta.get_field(code).verbose_name,
                        "children": [
                            {
                                "name": relation.related_word.name,
                                "score": relation.score
                            }
                            for relation in
                            results[code].order_by("-score")
                            ]
                    }
                    for code in codes
                ]
            }

            context['root_word'] = instance.name
            context['result_dict'] = result_dict

    # if a GET (or any other method) create a blank form
    else:
        form = RelatedWordsForm()

    # always add form to context
    context['form'] = form

    return render(request, 'words/visualization_related_words.html', context)


class WordSetDetailView(generic.DetailView):
    model = WordSet

    def get_context_data(self, **kwargs):
        context = super(WordSetDetailView, self).get_context_data()
        context['words_missing_data'] = self.object.words.filter(datamuse_success=False)
        return context


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

        # if user logged in, group wordsets by those created by user and all others
        user = self.request.user
        logger.debug(f'user: {user}')
        if user.is_authenticated:
            user_wordsets = WordSet.objects.filter(creator=user)
            other_wordsets = WordSet.objects.exclude(creator=user)
            context['user_wordsets'] = user_wordsets
            context['other_wordsets'] = other_wordsets

        return context


import json
import logging
import uuid

import django_rq
import redis
from coverage.xmlreport import os
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView
from rq.compat import text_type
from rq.job import Job
from rq.registry import StartedJobRegistry

from words.forms import RelatedWordsForm, WordSetCreateForm, WordSetChoice
from words.models import WordSet, Word

# Get an instance of a logger
logger = logging.getLogger(__name__)

# se up django-rq queue
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_cursor = redis.from_url(redis_url)    # singleton Redis client

# queue for running rq worker for WordSetCreateForm save
rq_queue = django_rq.get_queue('default', connection=redis_cursor)

# register to track running rq jobs
rq_started_job_registry = StartedJobRegistry(queue=rq_queue)  # connection=redis_cursor) #, queue=rq_queue)


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


class WordSetCreate(CreateView):
    """View to create a new WordSet"""
    model = WordSet
    form_class = WordSetCreateForm

    def __init__(self):
        super(WordSetCreate, self).__init__()

        # id to use for django-rq job for form processing
        self.job_id = text_type(uuid.uuid4())

    def get_form_kwargs(self):
        """Add request user to form kwargs"""
        kwargs = super(WordSetCreate, self).get_form_kwargs()

        # pass user to form so creator can be set to user
        kwargs['user'] = self.request.user

        # pass job_id for the form to use when creating a django-rq job
        kwargs['job_id'] = self.job_id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(WordSetCreate, self).get_context_data()
        context['navbar_wordset_create'] = 'active'
        return context

    def get_success_url(self):
        """Return the URL to redirect to. Redirects to page showing the progress of the WordSet creation."""
        logger.debug(f'start, job_id: {self.job_id}')
        return reverse('wordset_create_progress', kwargs={'pk': self.object.pk, 'job_id': self.job_id})


def wordset_create_progress_json(request, job_id):
    """Returns an rq job's progress (contained in job.meta) in json format."""
    job = Job.fetch(job_id, connection=redis_cursor)
    job.meta['status'] = job.get_status()
    job.save_meta()
    return JsonResponse(job.meta)


def wordset_create_progress(request, pk, job_id):
    """Displays the progress when processing the words for a new WordSet"""
    wordset = WordSet.objects.get(id=pk)
    logger.debug(f'wordset: {wordset.name}, job id: {job_id}')
    job = Job.fetch(job_id, connection=redis_cursor)

    context = {
        'wordset': wordset,
        'job': job,
        'job_id': job_id,
    }
    
    return render(request, 'words/wordset_create_progress.html', context)


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


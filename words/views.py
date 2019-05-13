from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from words.forms import WordForm
from words.models import WordSet


def index(request):
    """View function for home tab of site."""
    context = {
        "navbar_index": "active"   # make "Home" the active item in the navbar
               }

    return render(request, 'words/index.html', context)


def get_relation_viz(request):
    """View for the word relationship visualization"""
    context = {
        'viz_title': 'Word Relationships',  # Visualization title to use in page title
        'navbar_relation_viz': 'active'    # make "Word Relationships Visualization" the active item in the navbar
    }

    if request.method == 'POST':
        # create form instances and populate them with data from the request:
        word_form = WordForm(request.POST)

        if not request.user.is_authenticated:
            # no user logged in, get login information from auth_form
            auth_form = AuthenticationForm(request.POST)
            context['auth_form'] = auth_form

    # if a GET (or any other method) create a blank form
    else:
        word_form = WordForm()
        if not request.user.is_authenticated:
            # display blank login form, add it to context
            auth_form = AuthenticationForm()
            context['auth_form'] = auth_form

    # always add word_form to context
    context['word_form'] = word_form

    return render(request, 'words/visualization_generic.html', context)


class WordSetCreate(CreateView):
    """View to create a new WordSet"""
    model = WordSet
    fields = ['name', 'description']

    # todo get request. if user authenticated, set creator=user

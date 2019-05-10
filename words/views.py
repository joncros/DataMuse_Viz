from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from words.forms import WordForm
from words.models import WordSet


def index(request):
    """View function for home tab of site."""
    context = {
        # "index": "active"
               }

    return render(request, 'words/index.html', context)


def test_tab(request):
    """View to test a nav tab"""
    context = {
        # "test": "active"
    }

    return render(request, 'words/test_tab.html', context)


def viz_test(request):
    """View to test a nav tab"""
    context = {

    }

    return render(request, 'words/visualization_generic.html', context)


def get_relation_viz(request):
    """View for the word relationship visualization"""
    print('get_relation_viz')
    context = {}

    if request.method == 'POST':
        # create form instances and populate them with data from the request:
        word_form = WordForm(request.POST)
        if not request.user.is_authenticated:
            auth_form = AuthenticationForm(request)
            context['auth_form'] = auth_form

            # check whether auth_form valid
            if auth_form.is_valid():
                print('valid')
                # get user and login
                username = auth_form.cleaned_data['username']
                password = auth_form.cleaned_data['password']
                print(f'username: {username} password: {password}')
                user = authenticate(request, username=username, password=password)
                login(request, user)
            else:
                print('not valid')

    # if a GET (or any other method) create a blank form
    else:
        word_form = WordForm()
        if not request.user.is_authenticated:
            # display blank login form, add it to context
            auth_form = AuthenticationForm()
            context['auth_form'] = auth_form

    # always add word_form to context
    context['word_form'] = word_form

    # Default behavior (for GET requests) overridden if request is POST
    # word_form = WordForm()
    #
    # context = {
    #     'word_form': word_form,
    # }
    #
    # if not request.user.is_authenticated:
    #     # display login form if user not logged in
    #     # username = request.POST.get('username', '')
    #     # password = request.POST.get('password', '')
    #     # user = authenticate(request, username=username, password=password)
    #     # if user is not None:
    #     #     login(request, user)
    #     # else:
    #     #     return render(request, 'words/visualization_generic.html', context)
    #
    #     auth_form = AuthenticationForm()
    #
    #     context['auth_form'] = auth_form
    #
    # if request.method == 'POST':
    #     word_form = WordForm(request.POST)
    #     auth_form = AuthenticationForm(request.POST)
    #
    #     if auth_form.is_valid():
    #         login(request, auth_form.cleaned_data['user'])

        # if not auth_form.is_valid():
        #     return render('visualization_generic.html', {'auth_form': auth_form})


        #create Word form and populate

        # Check if the form(s) are valid and process
        #     login/logout if needed
        #     get relation type from WordForm
        #     query DataMuse
        #     display appropriate visualization
    # else:

    return render(request, 'words/visualization_generic.html', context)


class WordSetCreate(CreateView):
    model = WordSet
    fields = ['name', 'description']
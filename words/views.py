from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView

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


class WordSetCreate(CreateView):
    model = WordSet
    fields = ['name', 'description']

    def __init__(self):
        super(self).__init__()

    # def form_valid(self, form):
    #     if self.request.user
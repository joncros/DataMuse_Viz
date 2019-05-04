from django.shortcuts import render


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
# Views that belong to the whole project (currently re: user accounts)
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import generic

from datamuse_viz.forms import UserRegistrationForm


class UserRegistration(generic.CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/user_registration.html'


# def user_registration(request):
#     # If this is a POST request then process the Form data
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.Post)
#
#         # Check if the form is valid:
#         if form.is_valid():
#             # process the data in form.cleaned_data as required
#             new_user = form.cleaned_data
#             new_user.save()
#
#             # redirect to a new URL:
#             return HttpResponseRedirect(reverse('login'))
#
#     # If this is a GET (or any other method) crate the default form.
#     else:
#         form = UserRegistrationForm()
#
#     context = {
#         'form': form,
#     }
#
#     return render(request, 'registration/user_registration.html', context)
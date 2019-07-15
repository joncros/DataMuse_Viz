"""datamuse_viz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include

from datamuse_viz import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include URLs defined in words application
    path('words/', include('words.urls')),

    # Redirect base URL to words application
    path('', RedirectView.as_view(url='/words/', permanent=True)),
]

# Serve static files from /static/ folder during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),  # django built-in user account views
    path('accounts/registration/', views.UserRegistration.as_view(), name='user registration')  # user creation
]

# django-rq urls
urlpatterns += [
    path('django-rq/', include('django_rq.urls'))
]
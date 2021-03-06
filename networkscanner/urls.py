"""networkscanner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

# These are url:s that are used for django administration (Back-End)
# Known as url routing
# Caret ^ = Start of url
# Dollar sign $ = End of url
# If no url is matched, user is prompted with a 404 not found

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('scan.urls', namespace="scan")),
    url(r'^accounts/', include('registration.backends.default.urls')),
]

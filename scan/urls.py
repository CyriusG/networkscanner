from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^sites/$', views.sites, name='sites'),
    url(r'^sites/addsite/$', views.addsite, name='addsite'),
    url(r'^scan/scan/$', views.scan, name='scan'),
    url(r'^scan/addnetwork/$', views.addnetwork, name='addnetwork'),
    url(r'^scan/updatesite/$', views.updatesite, name='updatesite'),
]
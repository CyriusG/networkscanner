from django.conf.urls import url
from . import views

# These are url:s that are used for django administration (Back-End)
# Known as url routing
# Caret ^ = Start of url
# Dollar sign $ = End of url
# If no url is matched, user is prompted with a 404 not found
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^results/$', views.results, name='results'),
    url(r'^site/addsite/$', views.addsite, name='addsite'),
    url(r'^site/checksite/$', views.checksite, name='checksite'),
    url(r'^site/updatesite/(?P<site>.+)/$', views.updatesite, name='updatesite'),
    url(r'^scan/$', views.scan, name='scan'),
    url(r'^scan/addnetwork/$', views.addnetwork, name='addnetwork'),
    url(r'^scan/removenetwork/$', views.removenetwork, name='removenetwork'),
    url(r'^scan/checknetwork/$', views.checknetwork, name='checknetwork'),
    url(r'^scan/scannetwork/$', views.scannetwork, name='scannetwork'),
    url(r'^scan/discoveros/(?P<network_id>.+)/$', views.discoveros, name='discoveros'),
]

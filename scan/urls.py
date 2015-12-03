from django.conf.urls import url

from . import views

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
]
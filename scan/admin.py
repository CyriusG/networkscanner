from django.contrib import admin

from .forms import SiteForm
from .models import Scan, Network, Host, Service, Site, Siteuser
admin.site.register(Scan)
admin.site.register(Network)
admin.site.register(Host)
admin.site.register(Service)
admin.site.register(Site)
admin.site.register(Siteuser)
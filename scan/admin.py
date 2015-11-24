from django.contrib import admin

from .forms import SiteForm
from .models import Scan, Network, Host, Service, Site, Siteuser

class SiteAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "timestamp", "updated"]
    form = SiteForm

admin.site.register(Scan)
admin.site.register(Network)
admin.site.register(Host)
admin.site.register(Service)
admin.site.register(Site,SiteAdmin)
admin.site.register(Siteuser)
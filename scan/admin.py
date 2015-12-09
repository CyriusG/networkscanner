# Import defined models from scan/models.py
from django.contrib import admin
from .models import Scan, Network, Host, Service, Site, Siteuser

# Registration of models are done here, registered models appear in django administration
admin.site.register(Scan)
admin.site.register(Network)
admin.site.register(Host)
admin.site.register(Service)
admin.site.register(Site)
admin.site.register(Siteuser)

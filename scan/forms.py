from django import forms
# Imports the models defined from scan/models
from .models import Scan, Network, Site, Siteuser

# class ScanForm(forms.ModelForm):
#     # def __init__(self, site, *args, **kwargs):
#     #     super(ScanForm, self).__init__(*args, **kwargs)
#     #     self.fields['networks'].queryset = Network.objects.filter(site=site)
#
#     class Meta:
#         model = Scan
#         fields = ['networks']

# Structure of the form for defined models (in Django administration)
class NetworkForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = ['site', 'network_address', 'subnet_bits']

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name']

class SelectSiteForm(forms.ModelForm):
    class Meta:
        model = Siteuser
        fields = ['current_site']

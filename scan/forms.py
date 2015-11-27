from django import forms

from .models import Scan, Network, Site, Siteuser

class NetworkForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = ['site', 'network_address', 'subnet_bits']

# class ScanForm(forms.ModelForm):
#     # def __init__(self, site, *args, **kwargs):
#     #     super(ScanForm, self).__init__(*args, **kwargs)
#     #     self.fields['networks'].queryset = Network.objects.filter(site=site)
#
#     class Meta:
#         model = Scan
#         fields = ['networks']

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name']

class SelectSiteForm(forms.ModelForm):
    class Meta:
        model = Siteuser
        fields = ['current_site']
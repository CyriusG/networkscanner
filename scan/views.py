from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext
from celery.result import AsyncResult

from .forms import NetworkForm, ScanForm, SelectSiteForm, SiteForm
from .models import Scan, Site, Siteuser, Network
from .tasks import scanNetwork

@login_required
def index(request):

    list_of_sites = Site.objects.all()
    task_status = True
    select_site_form = SelectSiteForm()
    network_form = None
    scan_form = None
    sites_exists = True

    try:
        latest_scan = Scan.objects.latest('id')
        if latest_scan:
            task_status = AsyncResult(latest_scan.taskID).ready()
    except Scan.DoesNotExist:
        task_status = True
    try:
        selected_site = request.user.siteuser.current_site.name
    except Siteuser.DoesNotExist:
        selected_site = None

    try:
        network_form = NetworkForm()
        scan_form = ScanForm(request.user.siteuser.current_site)
    except Siteuser.DoesNotExist:
        sites_exists = False

    context = RequestContext(request, {
        'list_of_sites': list_of_sites,
        'selected_site': selected_site,
        'select_site_form': select_site_form,
        'network_form': network_form,
        'scan_form': scan_form,
        'task_status': task_status,
        'sites_exists': sites_exists,
    })
    return render(request, 'scan/index.html', context)

@login_required
def sites(request):
    sites_in_db = Site.objects.order_by('-id')[:20]
    site_form = SiteForm(request.POST or None)

    if site_form.is_valid():
        instance = site_form.save(commit=False)
        instance.save()

    context = RequestContext(request, {
        'sites_in_db': sites_in_db,
        'site_form': site_form,
    })
    return render(request, 'scan/sites.html', context)

@login_required
def addsite(request):
    if request.method == 'POST' and 'add_site' in request.POST:
        add_site_form = SiteForm(request.POST or None)
        if add_site_form.is_valid():
            add_site_form.save()
            data = add_site_form.cleaned_data
            site_name = data['name']
            try:
                Siteuser.objects.get(user=request.user)
            except Siteuser.DoesNotExist:
                site = Site.objects.get(name=site_name)
                site_user = Siteuser(user=request.user, current_site=site)
                site_user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def updatesite(request):
    if request.method == 'POST' and 'select_site' in request.POST:
        select_site_form = SelectSiteForm(request.POST or None)
        if select_site_form.is_valid():
            data = select_site_form.cleaned_data
            site = data['current_site']
            selected_site = Site.objects.get(name=site)
            try:
                Siteuser.objects.get(user=request.user)
            except Siteuser.DoesNotExist:
                site = Site.objects.get(name=site)
                site_user = Siteuser(user=request.user, current_site=site)
                site_user.save()
            current_user = Siteuser.objects.get(user=request.user)
            current_user.current_site = selected_site
            current_user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def addnetwork(request):
    if request.method == 'POST' and 'add_network' in request.POST:
        site = Network(site=request.user.siteuser.current_site)
        network_form = NetworkForm(request.POST or None, instance=site)
        if network_form.is_valid():
            network_form_instance = network_form.save(commit=False)
            network_form_instance.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def scan(request):
    try:
        latest_scan = Scan.objects.latest('id')
        latest_scan_status = latest_scan.ready
        if latest_scan_status:
            task_status = AsyncResult(latest_scan.taskID).ready()
    except Scan.DoesNotExist:
        task_status = True

    if request.method == 'POST' and 'scan_network' in request.POST:
       scan_form = ScanForm(request.user.siteuser.current_site, request.POST or None)
       if scan_form.is_valid() and task_status:
           scan_form_instance = scan_form.save(commit=False)
           scan_form_instance.site = request.user.siteuser.current_site
           scan_task = scanNetwork.delay(scan_form_instance.networks, scan_form_instance.site)
           scan_form_instance.taskID = scan_task.id
           scan_form_instance.ready = scan_task.ready()
           scan_form_instance.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
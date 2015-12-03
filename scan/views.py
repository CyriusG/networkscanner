from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from celery.result import AsyncResult

from .forms import NetworkForm, SelectSiteForm, SiteForm
from .models import Scan, Site, Siteuser, Network, Host, Service
from .tasks import scanNetwork

@login_required
def index(request):

    task_status = True
    network_form = None

    try:
        site_user = Siteuser.objects.get(user=request.user)
        current_site = site_user.current_site
    except Siteuser.DoesNotExist:
        try:
            default_site = Site.objects.get(default=True)
        except Site.DoesNotExist:
            default_site = Site(name="Default Site", default=True)
            default_site.save()
        site_user = Siteuser(user=request.user, current_site=default_site)
        site_user.save()
        current_site = default_site


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
        networks = Network.objects.all().order_by('-id').filter(site=current_site)[:20]
    except Network.DoesNotExist:
        networks = None

    networks_list = []

    if networks:
        for network in networks:
            network_list = []

            try:
                network_num_hosts = Host.objects.all().order_by('-id').filter(network__contains=network.id)
            except Host.DoesNotExist:
                network_num_hosts = None

            network_list.append(network)
            network_list.append(len(network_num_hosts))
            networks_list.append(network_list)

    try:
        hosts = Host.objects.all().order_by('-id').filter(site=current_site)[:20]
    except Siteuser.DoesNotExist:
        hosts = None

    hosts_list = []

    if hosts:
        for host in hosts:
            host_list = []

            try:
                host_num_services = Service.objects.all().order_by('-id').filter(host=host)
            except Service.DoesNotExist:
                host_num_services = None

            host_list.append(host)
            host_list.append(len(host_num_services))
            hosts_list.append(host_list)

    try:
        scans = Scan.objects.all().order_by('-id').filter(site=current_site)[:20]
    except Scan.DoesNotExist:
        scans = None

    scans_list = []

    if scans:
        for scan in scans:
            scan_list = []

            networks = scan.networks.split(',')

            try:
                networks = Network.objects.all().order_by('-id').filter(id__in=networks)
            except Network.DoesNotExist:
                networks = None

            scan_list.append(scan)
            scan_list.append(networks)
            scans_list.append(scan_list)

    try:
        sites = Site.objects.all().order_by('id')
    except Site.DoesNotExist:
        sites = None

    context = RequestContext(request, {
        'selected_site': selected_site,
        'network_form': network_form,
        'networks_list': networks_list,
        'hosts_list': hosts_list,
        'scans_list': scans_list,
        'sites': sites,
        'task_status': task_status,
    })
    return render(request, 'scan/overview.html', context)

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
def results(request):

    hosts = Host.objects.all().filter(site=request.user.siteuser.current_site)
    services = Service.objects.all().filter(host=hosts)

    try:
        sites = Site.objects.all().order_by('id')
    except Site.DoesNotExist:
        sites = None


    context = RequestContext(request, {
        'hosts_in_db': hosts,
        'services_in_db': services,
        'sites': sites
    })

    return render(request, 'scan/results.html', context)

@login_required
def addsite(request):
    if request.method == 'POST':
        site_name = request.POST['site_name']
        site = Site(name=site_name, default=False)
        site.save()
        try:
            Siteuser.objects.get(user=request.user)
        except Siteuser.DoesNotExist:
            site = Site.objects.get(name=site_name)
            site_user = Siteuser(user=request.user, current_site=site)
            site_user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def checksite(request):

    site_exist = False

    if request.method == 'GET':
        site = request.GET['site_name']
        try:
            Site.objects.get(name=site)
            site_exist = "True"
        except Site.DoesNotExist:
            site_exist = "False"

    return HttpResponse(site_exist)

@login_required
def updatesite(request, site):

    if site:
        site_user = request.user.siteuser
        try:
            new_site = Site.objects.get(name=site)
            site_user.current_site = new_site
            site_user.save()
        except Site.DoesNotExist:
            site_user = None

    # if request.method == 'POST' and 'select_site' in request.POST:
    #     select_site_form = SelectSiteForm(request.POST or None)
    #     if select_site_form.is_valid():
    #         data = select_site_form.cleaned_data
    #         site = data['current_site']
    #         selected_site = Site.objects.get(name=site)
    #         try:
    #             Siteuser.objects.get(user=request.user)
    #         except Siteuser.DoesNotExist:
    #             site = Site.objects.get(name=site)
    #             site_user = Siteuser(user=request.user, current_site=site)
    #             site_user.save()
    #         current_user = Siteuser.objects.get(user=request.user)
    #         current_user.current_site = selected_site
    #         current_user.save()

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

    if task_status:
        if request.method == 'POST' and 'scan_network' in request.POST:
            network_selected = request.POST['network_selected']
            site = request.user.siteuser.current_site
            task = scanNetwork.delay(network_selected, site)
            query = Scan(site=site,networks=network_selected, taskID=task.id, ready=task.ready())
            query.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
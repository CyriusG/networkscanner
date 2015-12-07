from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from celery.result import AsyncResult

# Import defied models from scan/models
from .models import Scan, Site, Siteuser, Network, Host, Service
from .tasks import scanNetwork

# This is the main connection between the back-end and front-end
# The different statements are further described in the text

# Authentication is used for this view
@login_required
def index(request):

    network_form = None
    # Use the current site to load information from
    try:
        site_user = Siteuser.objects.get(user=request.user)
        current_site = site_user.current_site
    # If no site have been created (new user), load "default site"
    except Siteuser.DoesNotExist:
        try:
            default_site = Site.objects.get(default=True)
        # If "default site" does not exist, create it
        except Site.DoesNotExist:
            default_site = Site(name="Default Site", default=True)
            default_site.save()
        site_user = Siteuser(user=request.user, current_site=default_site)
        site_user.save()
        current_site = default_site
    # Then list the latest scan for the site being used
    try:
        latest_scan = Scan.objects.latest('id')
        if latest_scan:
            task_status = AsyncResult(latest_scan.taskID).ready()
    # If no scan exist for the site try to list site user and site name instead.
    # If these are not present either, list nothing
    except Scan.DoesNotExist:
        task_status = True
    try:
        selected_site = request.user.siteuser.current_site.name
    except Siteuser.DoesNotExist:
        selected_site = None
    # Now list the 10 latest networks that were previously scanned
    # If there are no networks available, list nothing
    try:
        networks = Network.objects.all().order_by('-id').filter(site=current_site)[:10]
    except Network.DoesNotExist:
        networks = None

    networks_list = []
    # If there are networks available previously, list the number of host discovered for that network
    # If there are no hosts, list nothing
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
    # If hosts have been discovered, list the most recent 10
    # If no hosts exist, list nothing
    try:
        hosts = Host.objects.all().order_by('-id').filter(site=current_site)[:10]
    except Siteuser.DoesNotExist:
        hosts = None

    hosts_list = []
    # If there was hosts available, list the number of services found for each host
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
    # List the latest 10 scans if there are any
    try:
        scans = Scan.objects.all().order_by('-id').filter(site=current_site)[:10]
    except Scan.DoesNotExist:
        scans = None

    scans_list = []
    # In the list of scans, add a object for each nework that were scanned
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
    # Objects for this page, this makes it look nice when you zoooom (vector graphics)
    context = RequestContext(request, {
        'selected_site': selected_site,
        'network_form': network_form,
        'networks_list': networks_list,
        'hosts_list': hosts_list,
        'scans_list': scans_list,
        'sites': sites,
        'task_status': task_status,
    })
    # The result of this will be found in the overview tab of the web application
    return render(request, 'scan/overview.html', context)


# Authentication is used for this view
@login_required
def scan(request):
    # Use the current site to load information from
    try:
        site_user = Siteuser.objects.get(user=request.user)
        current_site = site_user.current_site
    # If no site have been created (new user), load "default site"
    except Siteuser.DoesNotExist:
        try:
            default_site = Site.objects.get(default=True)
        except Site.DoesNotExist:
            default_site = Site(name="Default Site", default=True)
            default_site.save()
        site_user = Siteuser(user=request.user, current_site=default_site)
        site_user.save()
        current_site = default_site
    # List the 20 latest scans executed for this site and user
    # If there are none, list nothing
    try:
        latest_scan = Scan.objects.latest('id')
        task_status = latest_scan.ready
    except Scan.DoesNotExist:
        task_status = True

    try:
        sites = Site.objects.all().order_by('id')
    except Site.DoesNotExist:
        sites = None

    # List the 20 latest networks created for this site
    try:
        networks = Network.objects.all().order_by('-id').filter(site=current_site)[:20]
    except Network.DoesNotExist:
        networks = None

    networks_list = []
    # List the number of hosts found for these networks if they have been scanned
    if networks:
        for network in networks:
            network_list = []

            try:
                network_num_hosts = Host.objects.all().order_by('-id').filter(network=network.id)
            except Host.DoesNotExist:
                network_num_hosts = None

            network_list.append(network)
            network_list.append(len(network_num_hosts))
            networks_list.append(network_list)
    # List the 10 latest network scans
    try:
        scans = Scan.objects.all().order_by('-id').filter(site=current_site)[:10]
    except Scan.DoesNotExist:
        scans = None

    scans_list = []
    # For the list of scans, create a object for the network that were scanned
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
    # Objects used for this page
    context = RequestContext(request, {
        'sites': sites,
        'networks_list': networks_list,
        'scans_list': scans_list,
        'task_status': task_status,
    })
    # This will be applied in the scan tab of the web application
    return render(request, 'scan/scan.html', context)

# Explain scannetwork here
@login_required
def scannetwork(request):

    try:
        latest_scan = Scan.objects.latest('id')
        latest_scan_status = latest_scan.ready
    except Scan.DoesNotExist:
        latest_scan_status = True

    if latest_scan_status:
        if request.method == 'POST':
            networks_id = request.POST.getlist('scan_network_id')

            for network in networks_id:
                hosts = Host.objects.all().filter(network=network)
                if len(hosts) > 0:
                    for host in hosts:
                        host.delete()

            task = scanNetwork.delay(networks_id, request.user.siteuser.current_site)
            query = Scan(site=request.user.siteuser.current_site,networks=','.join(networks_id), taskID=task.id, ready=task.ready())
            query.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Explain addnetwork here
@login_required
def addnetwork(request):
    if request.method == 'POST':
        network_address = request.POST['network_address']
        subnet_bits = request.POST['subnet_bits']
        site = request.user.siteuser.current_site
        network = Network(site=site, network_address=network_address, subnet_bits=subnet_bits)
        network.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Explain remove network here
@login_required
def removenetwork(request):
    if request.method == 'POST':
        network_id = request.POST['network_id']

        try:
            networks = Network.objects.get(id=network_id)
            networks.delete()
        except Network.DoesNotExist:
            networks = None

        try:
            hosts = Host.objects.all().filter(network=network_id)
            for host in hosts:
                host.delete()
        except Host.DoesNotExist:
            hosts = None

        scans = Scan.objects.all().filter(networks__contains=network_id)

        for scan in scans:
            networks = scan.networks.split(',')

            if len(networks) == 1:
                scan.delete()
            else:
                new_networks = []
                for network in networks:
                    if network != network_id:
                        new_networks.append(str(network))
                new_networks = ','.join(network_join for network_join in new_networks)
                scan.networks = str(new_networks)
                scan.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Explain checknetwork here
@login_required
def checknetwork(request):

    network_exist = False

    if request.method == 'GET':
        network_address = request.GET['network']
        subnet_bits = request.GET['subnet']
        try:
            Network.objects.get(site=request.user.siteuser.current_site, network_address=network_address, subnet_bits=subnet_bits)
            network_exist = "True"
        except Network.DoesNotExist:
            network_exist = "False"

    return HttpResponse(network_exist)

# Explain results here
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

# Explain addsite here
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

# Explain checksite here
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

# Explain updatesite here
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

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

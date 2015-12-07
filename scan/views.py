from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from celery.result import AsyncResult

# Import defined models from scan/models

from .models import Scan, Site, Siteuser, Network, Host, Service
from .tasks import scanNetwork

@login_required
def index(request):

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
        networks = Network.objects.all().order_by('-id').filter(site=current_site)[:10]
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
        hosts = Host.objects.all().order_by('-id').filter(site=current_site)[:10]
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
        scans = Scan.objects.all().order_by('-id').filter(site=current_site)[:10]
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
        'networks_list': networks_list,
        'hosts_list': hosts_list,
        'scans_list': scans_list,
        'sites': sites,
        'task_status': task_status,
    })

    return render(request, 'scan/overview.html', context)

@login_required
def scan(request):
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
        task_status = latest_scan.ready
    except Scan.DoesNotExist:
        task_status = True

    try:
        sites = Site.objects.all().order_by('id')
    except Site.DoesNotExist:
        sites = None


    try:
        networks = Network.objects.all().order_by('-id').filter(site=current_site)[:20]
    except Network.DoesNotExist:
        networks = None

    networks_list = []

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

    try:
        scans = Scan.objects.all().order_by('-id').filter(site=current_site)[:10]
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

    context = RequestContext(request, {
        'sites': sites,
        'networks_list': networks_list,
        'scans_list': scans_list,
        'task_status': task_status,
    })

    return render(request, 'scan/scan.html', context)

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

@login_required
def addnetwork(request):
    if request.method == 'POST':
        network_address = request.POST['network_address']
        subnet_bits = request.POST['subnet_bits']
        site = request.user.siteuser.current_site
        network = Network(site=site, network_address=network_address, subnet_bits=subnet_bits)
        network.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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


@login_required
def results(request):

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
        task_status = latest_scan.ready
    except Scan.DoesNotExist:
        task_status = True

    try:
        sites = Site.objects.all().order_by('id')
    except Site.DoesNotExist:
        sites = None

    results = []

    try:
        networks = Network.objects.all().filter(site=current_site)
    except Network.DoesNotExist:
        networks = None

    if networks:
        for network in networks:
            result = []
            hosts = []

            try:
                hosts_objects = Host.objects.all().filter(network=network.id)
            except Host.DoesNotExist:
                hosts_objects = None

            if hosts_objects:
                for host in hosts_objects:

                    host_objects = []
                    services = []

                    try:
                        services_objects = Service.objects.all().filter(host=host)
                    except Service.DoesNotExist:
                        services_objects = None

                    if services_objects:
                        for service in services_objects:
                            services.append(service)

                    host_objects.append(host)
                    host_objects.append(services)
                    host_objects.append(len(services))

                    hosts.append(host_objects)

            result.append(network)
            result.append(hosts)

            results.append(result)
    else:
        results = None

    context = RequestContext(request, {
        'results': results,
        'sites': sites,
        'task_status': task_status,
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

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

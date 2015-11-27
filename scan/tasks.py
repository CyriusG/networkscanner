from BeautifulSoup import BeautifulSoup
from celery import Celery
import commands

from .models import Network, Host, Site, Service, Scan

app = Celery('tasks', backend='amqp', broke='amqp://guest@localhost//')

@app.task(bind=True)
def scanNetwork(self, network, site):

    network = str(network)

    network_address, subnet_bits = network.split("/")

    site_object = Site.objects.get(name=site)
    network_object = Network.objects.get(site=site_object, network_address=network_address, subnet_bits=subnet_bits)

    nmap_output = commands.getoutput("nmap -oX - %s" % network)
    xml_soup = BeautifulSoup(nmap_output)
    if xml_soup:
        for q in xml_soup.findAll("host"):
            if q:
                q_ip = q.findAll("address")
                if q_ip:
                    ip = q.address.get("addr")
                q_hostname = q.hostnames.findAll("hostname")
                if q_hostname:
                    hostname = q.hostname.get("name")
                else:
                    hostname = " "
                services = []
                q_port = q.findAll("port")
                if q_port:
                    for z in q_port:
                        service = []
                        service.append(z.get("portid"))
                        service.append(z.get("protocol"))
                        service.append(z.find("state").get("state"))
                        service.append(z.find("service").get("name"))
                        services.append(service)
                if site_object and ip and network_object and hostname:
                    host = Host(site=site_object, ip=ip, network=network_object, dnsName=hostname)
                    host.save()
                    for j, item in enumerate(services):
                        query = Service(host=host, portID=services[j][0], protocol=services[j][1], state=services[j][2], serviceName=services[j][3])
                        query.save()

    current_scan = Scan.objects.get(taskID=self.request.id)
    current_scan.ready = True
    current_scan.save()

    return('Done')
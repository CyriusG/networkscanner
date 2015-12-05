from BeautifulSoup import BeautifulSoup
from celery import Celery
import commands

from .models import Network, Host, Site, Service, Scan

app = Celery('tasks', backend='amqp', broke='amqp://guest@localhost//')

@app.task(bind=True)
def scanNetwork(self, networks, site):
    for network in networks:
        network = Network.objects.get(id=network)
        network_address = network.network_address
        subnet_bits = network.subnet_bits
        network_nmap = network_address + "/" + subnet_bits

        nmap_output = commands.getoutput("nmap -oX - %s" % network_nmap)
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
                    if site and ip and network and hostname:
                        host = Host(site=site, ip=ip, network=network.id, dnsName=hostname)
                        host.save()
                        for j, item in enumerate(services):
                            query = Service(host=host, portID=services[j][0], protocol=services[j][1], state=services[j][2], serviceName=services[j][3])
                            query.save()

    current_scan = Scan.objects.get(taskID=self.request.id)
    current_scan.ready = True
    current_scan.save()

    return('Done')
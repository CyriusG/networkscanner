from django.contrib.auth.models import User
from django.db import models

class Site(models.Model):
    name = models.CharField(max_length=200, unique=True, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    def __unicode__(self):
        return self.name

class Siteuser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_site = models.ForeignKey(Site)
    def __unicode__(self):
        return self.user.username + ":" + self.current_site.name

class Network(models.Model):
    site = models.ForeignKey(Site)
    network_address = models.GenericIPAddressField(blank=False, null=False)
    subnet_bits = models.CharField(max_length=2)
    class Meta:
        unique_together = ('site', 'network_address', 'subnet_bits')
    def __unicode__(self):
        return 'id:' + str(self.id) + ': ' + self.network_address + "/" + str(self.subnet_bits)

class Scan(models.Model):
    site = models.ForeignKey(Site, null=False, blank=False)
    networks = models.CharField(max_length=200)
    taskID = models.CharField(max_length=200)
    ready = models.BinaryField()
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    def __unicode__(self):
        return self.site.name + ", " + self.taskID + ", " + str(self.ready)

class Host(models.Model):
    site = models.ForeignKey(Site)
    ip = models.CharField(max_length=15)
    network = models.CharField(max_length=200)
    dnsName = models.CharField(max_length=200)
    def __unicode__(self):
		return 'IP: ' + self.ip + ' Network: ' + self.network + ' Hostname: ' + self.dnsName

class Service(models.Model):
    host = models.ForeignKey(Host)
    portID = models.CharField(max_length=5)
    protocol = models.CharField(max_length=10)
    state = models.CharField(max_length=10)
    serviceName = models.CharField(max_length=200)
    def __unicode__(self):
        return ' Host: ' + self.host.ip + ':' + self.portID + '/' + self.protocol + " (" + self.serviceName + ":" + self.state + ")"

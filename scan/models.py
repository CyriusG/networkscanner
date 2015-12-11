from django.contrib.auth.models import User
from django.db import models

# This is where data is stored

# Definition for the site model
# Contains a name for user reference, a timestamp which indicates when it was created
# and another field for when it was last updated.
class Site(models.Model):
    name = models.CharField(max_length=200, unique=True, null=False, blank=False)
    default = models.BinaryField()
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    def __unicode__(self):
        return self.name + " Default: " + str(self.default)

# Model for associating a user with a site.
class Siteuser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_site = models.ForeignKey(Site)
    def __unicode__(self):
        return self.user.username + ":" + self.current_site.name

# Each network entry contains a record which points at the site object,
# what network address and subnet bits the network that is being defined has
# and a timestamp to indicate when it was created.
class Network(models.Model):
    site = models.ForeignKey(Site, null=False, blank=False)
    network_address = models.GenericIPAddressField(blank=False, null=False)
    subnet_bits = models.CharField(max_length=2)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    class Meta:
        unique_together = ('site', 'network_address', 'subnet_bits')
    def __unicode__(self):
        return 'id:' + str(self.id) + ': ' + self.network_address + "/" + str(self.subnet_bits)

# Database entry which points at what site a scan belongs to, what networks that are being scanned
# in a comma separated integer format so that multiple networks can be referenced
# if it is ready (true/false) and timestamps to indicate when it was created and when it was last updated.
class Scan(models.Model):
    site = models.ForeignKey(Site, null=False, blank=False)
    networks = models.CommaSeparatedIntegerField(max_length=200)
    taskID = models.CharField(max_length=200)
    ready = models.BinaryField()
    host_discovery = models.BinaryField()
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    def __unicode__(self):
        return self.site.name + ", " + self.taskID + ", " + str(self.ready) + ", " + str(self.host_discovery)

# Points at what site the host belongs to, what IP it has, what network as a single integer field, its hostname
# and a timestamp to indicate when it was added.
class Host(models.Model):
    site = models.ForeignKey(Site, null=False, blank=False)
    ip = models.CharField(max_length=15)
    network = models.IntegerField(null=False, blank=False)
    dnsName = models.CharField(max_length=200, blank=True, null=True)
    os = models.CharField(max_length=200, blank=True, null=True, default="unknown")
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    def __unicode__(self):
		return 'IP: ' + self.ip + ' Hostname: ' + self.dnsName

# Points at what host the service belongs to, what the port is, what protocol, what the state of the port is and
# what the service is called.
class Service(models.Model):
    host = models.ForeignKey(Host, null=False, blank=False)
    portID = models.CharField(max_length=5)
    protocol = models.CharField(max_length=10)
    state = models.CharField(max_length=10)
    serviceName = models.CharField(max_length=200)
    def __unicode__(self):
        return ' Host: ' + self.host.ip + ':' + self.portID + '/' + self.protocol + " (" + self.serviceName + ":" + self.state + ")"

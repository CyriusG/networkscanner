# networkscanner

Networkscanner project.

# Deployment

### Software requirements

* Python
* Django, Celery, BeautifulSoup and Django Crispy Forms Python modules
* A web server (instructions for Apache included here)
* A database server (instructions for MySQL/MariaDB included)
* RabbitMQ

### Installation

Most Linux distributions comes with Python and Python pip installed, if not, follow the instructions for your distribution to install these packages.

Install the required Python modules:
  
```
pip install django celery beautifulsoup djang-crispy-forms
```

Installing the servers that is required for the application. Both CentOS 7 and Debian instructions will be shown.

**CentOS 7:**

Install the servers:

```
yum install -y httpd mariadb-server rabbitmq-server
```

Enable the services:

```
systemctl enable httpd mariadb rabbitmq-server
```

Start the services:

```
systemctl start httpd mariadb rabbitmq-server
```

**Debian:**

Install Apache and MariaDB:

```
apt-get install -y apache2 mariadb-server
```

Install RabbitMQ (Copied from the RabbitMQ documentation https://www.rabbitmq.com/install-debian.html)

```
Add the following line to your /etc/apt/sources.list: 
deb http://www.rabbitmq.com/debian/ testing main

To avoid warnings about unsigned packages, add our public key to your trusted key
list using apt-key(8): 
wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
sudo apt-key add rabbitmq-signing-key-public.asc

Run apt-get update. 
Install packages as usual; for instance, 
sudo apt-get install rabbitmq-server
```

Enable the services:

```
systemctl enable apache2 mariadb rabbitmq-server
```

Start the serivces:

```
systemctl start apache2 mariadb rabbitmq-server
```

### Configure Apache

A working configuration is attached below, change {root diretory} to where you are going to put the web application.

```apache
WSGIPythonPath {root diretory}/networkscanner

Alias /robots.txt {root diretory}/networkscanner/static/robots.txt
Alias /favicon.ico {root diretory}/networkscanner/static/favicon.ico

Alias /media/ {root diretory}/networkscanner/media/
Alias /static/ {root diretory}/networkscanner/static/static_root/

<Directory {root diretory}/networkscanner/static/static_root>
        Require all granted
</Directory>

<Directory {root diretory}/networkscanner/media>
        Require all granted
</Directory>

WSGIScriptAlias / {root diretory}/networkscanner/networkscanner/wsgi.py

<Directory {root diretory}/networkscanner/networkscanner>
        <Files wsgi.py>
                Require all granted
        </Files>
</Directory>
```

Open the ports required for Apache.

```
firewall-cmd --zone=public --add-port 80/tcp --permanent
firewall-cmd --reload
```

### Configure MySQL/MariaDB

Sign in into the management console:

```s
mysql -u root
```

Create the database and add a user to it, don't forget to change {username} and {password}:

```sql
CREATE DATABASE networkscanner;
GRANT ALL ON networkscanner.* TO {username}@localhost IDENTIFIED BY '{password}';
```

### Download the application

Go to the web root directory as specified in the Apache configuration file, /var/www/html in this case.

```
cd /var/www/html/
```

Clone the application:

```
git clone https://github.com/CyriusG/networkscanner.git
```

### Configure the application database settings

Edit the file settings.py located in networkscanner/ using your editor of choice, I'm using vim.

```
vim networkscanner/networkscanner/settings.py
```

Locate the database settings and change them to what you called the user which is assigned to the database:

```python
...
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'networkscanner',
        'USER': '{username}',
        'PASSWORD': '{password}',
        'HOST': 'localhost',
    }
}
...
```

### Populate the database and create a superuser

Now when the database is configured all that is left is to populate the database and add a superuser.

Change directory to the application root directory.

```
cd networkscanner/
```

Populate the database and add a superuser.

```
python manage.py migrate
python manage.py createsuperuser
```

### Configure the Celery worker

Paste the following code into /usr/lib/systemd/system/celery.service, make sure to change {working directory} to the root directory of the application. Make sure that you also create the /var/run/celery and /var/log/celery directories, otherwise the worker will not start.

```systemd
[Unit]
Description=Celery workers
After=network.target

[Service]
Type=forking
User=root
Group=root
WorkingDirectory={working directory}
Environment="C_FORCE_ROOT=true"
ExecStart=/usr/bin/celery multi start w1 \
    -A networkscanner --pidfile=/var/run/celery/%N.pid \
    --logfile=/var/log/celery/%N.log --loglevel="info" \
    --time-limit=300 --concurrency=2
ExecStop=/usr/bin/celery multi stopwait w1 \
    --pidfile=/var/run/celery/%N.pid
ExecReload=/usr/bin/celery multi restart w1 \
    -A networkscanner --pidfile=/var/run/celery/%N.pid \
    --logfile=/var/log/celery/%N.log --loglevel="info" \
    --time-limit=300 --concurrency=2

[Install]
WantedBy=multi-user.target
```

Enable the worker:

```
systemctl enable celery
```

Start the worker:

```
systemctl start celery
```

### Deployment complete!

You should now be able to browse to the IP of the server and start using the application.

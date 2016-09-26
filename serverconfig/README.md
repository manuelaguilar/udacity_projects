# LINUX Server Configuration Project

## Server details
- Server IP: 52.36.231.98
- SSH port: 2200
- Application URL: http://ec2-52-36-231-98.us-west-2.compute.amazonaws.com/catalog

## Software packages (installed)
- Package repositories updated
- Software packages updated (reboot pending)
  - apg - for password generation
```
apg -m15 -M SNC
```
  - ntp - ntp time server 
  - postgresql
  - python-psycopg2
  - python-flask
  - python-sqlalchemy
  - python-pip
  - libapache2-mod-wsgi
  - bleach (pip install)
  - oauth2client (pip install)
  - requests (pip install)
  - httplib2 (pip install)
  - redis (pip install)
  - passlib (pip install)
  - itsdangerous (pip install)
  - flask-httpauth (pip install)
  - git

## Server configuration

- Public key copied from root account into .ssh directory for users grader, manuel, 
and catalogadmin
- For each user files created and permissions updated
```
chmod 700 ~/.ssh
chmod 400 ~/.ssh/authorized_keys
```
- SSH port changed to 2200
- Users created: 
  - manuel (sudo, PASSWD)
  - grader (sudo, PASSWD)
  - catalogadmin (no sudo)
- Remote login disabled
- Remove clear password login disabled
- Server timezone changed to : UTC
- NTP server up
- Firewall enabled
  - Rules
```
To                         Action      From
--                         ------      ----
2200/tcp                   ALLOW       Anywhere
80                         ALLOW       Anywhere
123                        ALLOW       Anywhere
2200/tcp (v6)              ALLOW       Anywhere (v6)
80 (v6)                    ALLOW       Anywhere (v6)
123 (v6)                   ALLOW       Anywhere (v6)
```
- Apache 2 server: /etc/apache2/sites-enabled/000-default.conf
  - VirtualHost
```
        ServerName ec2-52-36-231-98.us-west-2.compute.amazonaws.com
        ServerAdmin manuel.aguilar.alvarez@gmail.com
        DocumentRoot /home/catalogadmin/www/
```
  - WSGI module enabled
```
    WSGIScriptAlias /   /var/www/html/myapp.wsgi
    WSGIDaemonProcess student user=student group=student processes=2 threads=2 stack-size=524288
    WSGIProcessGroup student
``` 
- postgresql
  - Users created: 
    - catalog
  - No external connections allowed
  - Database: productcatalog


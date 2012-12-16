
Alias /favicon.ico /usr/local/imageapi/mgmt/main/static/favicon.ico
Alias /robots.txt /usr/local/imageapi/mgmt/main/static/robots-prod.txt
Alias /sitemap.xml /usr/local/imageapi/mgmt/main/static/sitemap.xml
Alias /static /usr/local/imageapi/mgmt/main/static

<VirtualHost *:80>
	ServerAdmin webmaster@localhost
	ServerName www.trollaface.com

	DocumentRoot /var/www/

	WSGIScriptAlias / /usr/local/imageapi/mgmt/django.wsgi

	# disable direcory listening
	Options -Indexes

	ErrorLog /var/log/apache2/error.log
	
	# Possible values include: debug, info, notice, warn, error, crit,
	# alert, emerg.
	LogLevel warn

	LogFormat "%{X-Forwarded-For}i %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" imageapi_combined
	
	CustomLog /var/log/apache2/access.log imageapi_combined
	
</VirtualHost>

<VirtualHost *:80>
	ServerAdmin webmaster@localhost
	ServerName trollaface.com

	RedirectPermanent / http://www.trollaface.com
</VirtualHost>

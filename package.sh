#!/bin/bash

base_dir=`pwd`
package_dir="$base_dir/package"
app_dir="$package_dir/usr/local/imageapi"

# Get our release version from settings.py
version=`grep '^VERSION =' $base_dir/mgmt/settings.py | sed 's/[^0-9\.]//g'`
deb_file="imageapi-${version}_all.deb"

# create temporary folder for packaging
rm -r $package_dir
mkdir -p $package_dir/DEBIAN

echo "Creating Debian control file..."
cat resources/debian/control_template | sed "s/\$VERSION/$version/" > $package_dir/DEBIAN/control
cp resources/debian/conffiles resources/debian/postinst resources/debian/prerm resources/debian/postrm $package_dir/DEBIAN

echo "Copying project files..."

# App
mkdir -p $package_dir/usr/local/imageapi
mkdir -p $package_dir/etc/imageapi
#cp resources/etc/imageapi.conf $package_dir/etc/imageapi
tar -c --exclude='*.svn*' --exclude "*.pyc" --exclude="package" -f - mgmt api | (cd $package_dir/usr/local/imageapi; tar -xf -)

# Apache
mkdir -p $package_dir/etc/apache2/sites-available
cp resources/apache/sites-available/* $package_dir/etc/apache2/sites-available


# rsyslog
#mkdir -p $package_dir/etc/rsyslog.d/
#cp resources/rsyslog/99-imageapi.conf $package_dir/etc/rsyslog.d

# logrotate
#mkdir -p $package_dir/etc/logrotate.d/
#cp resources/logrotate/imageapi $package_dir/etc/logrotate.d


echo "Building ImageAPI core Debian package..."

#chgrp -R bmm $package_dir/{etc,usr,var}
#chmod -R g+ws $package_dir/{etc,usr,var}
dpkg-deb -b $package_dir $base_dir/dist/deb/$deb_file

echo "Uploading to Server /tmp/$deb_file"
scp "$base_dir/dist/deb/$deb_file" "sf@ec2-23-20-121-26.compute-1.amazonaws.com:/tmp/"



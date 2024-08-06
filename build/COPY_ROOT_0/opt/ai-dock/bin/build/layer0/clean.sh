#!/bin/false

# Tidy up and keep image small
apt-get clean -y

fix-permissions.sh -o container
rm /etc/ld.so.cache
ldconfig
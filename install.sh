#!/bin/bash

echo "======================================"
echo "Detect Presence ARP - Installation"
echo "======================================"

echo ""
echo "Updating package list..."
apt update

echo ""
echo "Installing arp-scan..."
apt install -y arp-scan

echo ""
echo "Checking vendor files..."

mkdir -p /usr/share/arp-scan

if [ ! -f /usr/share/arp-scan/mac-vendor.txt ]; then
    touch /usr/share/arp-scan/mac-vendor.txt
    chmod 644 /usr/share/arp-scan/mac-vendor.txt
    echo "Created mac-vendor.txt"
fi

if [ -f /usr/share/arp-scan/ieee-oui.txt ]; then
    chmod 644 /usr/share/arp-scan/ieee-oui.txt
    echo "ieee-oui.txt permissions OK"
fi

echo ""
echo "arp-scan path:"

which arp-scan

echo ""
echo "Testing arp-scan..."

arp-scan --localnet | head -10

echo ""
echo "======================================"
echo "Installation finished."
echo "Restart Domoticz if needed."
echo "======================================"
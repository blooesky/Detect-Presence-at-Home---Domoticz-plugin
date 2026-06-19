Detect Presence at Home

Domoticz plugin for presence detection using phone MAC addresses and arp-scan.

Features
Automatic detection of arp-scan
Optional automatic installation of arp-scan
Multiple phones support
One switch for each phone
Anyone Home switch
Presence Status text sensor
Last Seen text sensor for each phone
Configurable polling interval
Configurable timeout before marking a device as away
Installation

Clone the repository into the Domoticz plugins folder:

cd /home/pi/domoticz/plugins
git clone https://github.com/YOUR_USER/detect_presence_arp.git

Optional:

sudo bash /home/pi/domoticz/plugins/detect_presence_arp/install.sh

Restart Domoticz:

sudo systemctl restart domoticz



Configuration

Add a new Hardware device:

Type
Detect Presence ARP


Phones

Example:
Geo=AA:BB:CC:DD:EE:FF, Cristina=11:22:33:44:55:66

Poll interval seconds
Recommended:
20

Miss count before Away
Recommended:
120


Interface optional

Leave auto or specify:
eth0
or
wlan0

Devices created automatically

Example:

Geo                    Switch
Geo Last Seen          Text

Cristina               Switch
Cristina Last Seen     Text

Anyone Home            Switch

Presence Status        Text
Notes

For best results disable Random/Private MAC on phones connected to your home Wi-Fi.

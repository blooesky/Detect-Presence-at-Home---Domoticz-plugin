# Detect Presence at Home

Domoticz plugin for home presence detection using phone MAC addresses and `arp-scan`.

## Features

* Automatic detection of `arp-scan`
* Optional automatic installation of `arp-scan`
* Support for multiple phones
* One switch for each phone
* `Anyone Home` switch
* `Presence Status` text sensor
* `Last Seen` text sensor for each phone
* Configurable polling interval
* Configurable away timeout in seconds
* Optional network interface selection:

  * Auto
  * eth0
  * wlan0

## Installation

Clone the repository into the Domoticz plugins folder:

```bash
cd /home/pi/domoticz/plugins
git clone https://github.com/blooesky/Detect-Presence-at-Home---Domoticz-plugin.git detect_presence_arp
```

Optional:

```bash
sudo bash /home/pi/domoticz/plugins/detect_presence_arp/install.sh
```

Restart Domoticz:

```bash
sudo systemctl restart domoticz
```

## Configuration

Add a new Hardware device.

### Type

```text
Detect Presence at home
```

### Phones

Example:

```text
Andy=AA:BB:CC:DD:EE:FF, Cristina=11:22:33:44:55:66
```

### Poll interval seconds

Recommended:

```text
20
```

### Away timeout seconds

Recommended:

```text
120
```

### Network interface

Leave **Auto** or select:

```text
eth0
```

or

```text
wlan0
```

## Devices created automatically

Example:

```text
Andy                   Switch
Andy Last Seen          Text

Cristina               Switch
Cristina Last Seen     Text

Anyone Home            Switch

Presence Status        Text
```

## Notes

For best results, disable **Random/Private MAC** on phones connected to your home Wi-Fi network.


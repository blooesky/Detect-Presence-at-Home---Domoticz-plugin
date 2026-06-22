# Presence at home ARP Detect - Domoticz Plugin

"""
<plugin key="detect_presence_arp" name="Detect Presence At Home - ARP" author="4D" version="1.0.2" wikilink="https://github.com/blooesky/Detect-Presence-at-Home---Domoticz-plugin">
    <params>
        <param field="Mode1" label="Phones" width="600px" required="true" default="Andy=AA:BB:CC:DD:EE:FF, Cristina=11:22:33:44:55:66"/>
        <param field="Mode2" label="Poll interval seconds" width="100px" required="true" default="20"/>
        <param field="Mode3" label="Away timeout seconds" width="120px" required="true" default="120"/>
        <param field="Mode4" label="Network interface" width="120px">
            <options>
                <option label="Auto" value="" default="true"/>
                <option label="eth0" value="eth0"/>
                <option label="wlan0" value="wlan0"/>
            </options>
        </param>
        <param field="Mode5" label="Auto install arp-scan" width="100px">
            <options>
                <option label="No" value="No"/>
                <option label="Yes" value="Yes" default="true"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="False" value="False" default="true"/>
                <option label="True" value="True"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import subprocess
import shutil
import re
import time
from datetime import datetime

UNIT_ANYONE = 1
UNIT_STATUS = 2
FIRST_PHONE_UNIT = 10

class PresenceARP:
    def __init__(self):
        self.phones = []
        self.arp_path = None
        self.poll_interval = 20
        self.away_timeout = 120
        self.interface = ""
        self.last_poll = 0
        self.last_seen_text = {}
        self.last_seen_ts = {}

    def onStart(self):
        if Parameters["Mode6"] == "True":
            Domoticz.Debugging(1)

        self.phones = self.parse_phones(Parameters["Mode1"])
        self.poll_interval = self.to_int(Parameters["Mode2"], 20)
        self.away_timeout = self.to_int(Parameters["Mode3"], 120)
        self.interface = Parameters["Mode4"].strip()
        auto_install = Parameters["Mode5"] == "Yes"

        self.arp_path = shutil.which("arp-scan")

        if not self.arp_path and auto_install:
            Domoticz.Log("arp-scan not found. Trying auto install...")
            self.install_arp_scan()
            self.arp_path = shutil.which("arp-scan")

        if not self.arp_path:
            Domoticz.Error("arp-scan not found. Run manually: sudo apt update && sudo apt install -y arp-scan")
        else:
            Domoticz.Log("Using arp-scan: " + self.arp_path)

        self.create_devices()
        Domoticz.Heartbeat(5)
        self.scan()

    def to_int(self, value, default):
        try:
            return int(str(value).strip())
        except Exception:
            return default

    def install_arp_scan(self):
        try:
            subprocess.call(["sudo", "apt", "update"], timeout=120)
            subprocess.call(["sudo", "apt", "install", "-y", "arp-scan"], timeout=180)
            subprocess.call(["sudo", "touch", "/usr/share/arp-scan/mac-vendor.txt"], timeout=10)
            subprocess.call(["sudo", "chmod", "644", "/usr/share/arp-scan/mac-vendor.txt"], timeout=10)
        except Exception as e:
            Domoticz.Error("Auto install failed: " + str(e))

    def normalize_mac(self, mac):
        mac = mac.strip().lower().replace("-", ":")
        parts = mac.split(":")
        if len(parts) == 6:
            return ":".join(p.zfill(2) for p in parts)
        return mac

    def parse_phones(self, raw):
        result = []

        for item in raw.split(","):
            item = item.strip()
            if not item:
                continue

            if "=" not in item:
                Domoticz.Error("Invalid phone entry: " + item)
                continue

            name, mac = item.split("=", 1)
            name = name.strip()
            mac = self.normalize_mac(mac)

            if not re.match(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$", mac):
                Domoticz.Error("Invalid MAC for " + name + ": " + mac)
                continue

            result.append({
                "name": name,
                "mac": mac
            })

        return result

    def create_devices(self):
        if UNIT_ANYONE not in Devices:
            Domoticz.Device(
                Name="Anyone Home",
                Unit=UNIT_ANYONE,
                TypeName="Switch"
            ).Create()

        if UNIT_STATUS not in Devices:
            Domoticz.Device(
                Name="Presence Status",
                Unit=UNIT_STATUS,
                TypeName="Text"
            ).Create()

        for i, phone in enumerate(self.phones):
            switch_unit = FIRST_PHONE_UNIT + i * 2
            seen_unit = switch_unit + 1

            if switch_unit not in Devices:
                Domoticz.Device(
                    Name=phone["name"],
                    Unit=switch_unit,
                    TypeName="Switch"
                ).Create()

            if seen_unit not in Devices:
                Domoticz.Device(
                    Name=phone["name"] + " Last Seen",
                    Unit=seen_unit,
                    TypeName="Text"
                ).Create()

            self.last_seen_text[phone["mac"]] = "Never"
            self.last_seen_ts[phone["mac"]] = 0

    def onHeartbeat(self):
        now = time.time()

        if now - self.last_poll >= self.poll_interval:
            self.last_poll = now
            self.scan()

    def run_scan(self):
        if not self.arp_path:
            return ""

        cmd = [self.arp_path]

        if self.interface:
            cmd += ["--interface", self.interface]

        cmd += ["--localnet"]

        try:
            out = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                timeout=25
            ).decode("utf-8", "ignore")

            return out.lower().replace("-", ":")

        except Exception as e:
            Domoticz.Error("arp-scan failed: " + str(e))
            return ""

    def scan(self):
        output = self.run_scan()
        if not output:
            return

        now = time.time()
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        present_names = []

        for i, phone in enumerate(self.phones):
            mac = phone["mac"]
            name = phone["name"]

            switch_unit = FIRST_PHONE_UNIT + i * 2
            seen_unit = switch_unit + 1

            found = mac in output

            if found:
                self.last_seen_ts[mac] = now
                self.last_seen_text[mac] = now_text
                present = True
            else:
                last_seen = self.last_seen_ts.get(mac, 0)
                present = last_seen > 0 and (now - last_seen) <= self.away_timeout

            if present:
                present_names.append(name)

            if switch_unit in Devices:
                Devices[switch_unit].Update(
                    nValue=1 if present else 0,
                    sValue="On" if present else "Off"
                )

            if seen_unit in Devices:
                Devices[seen_unit].Update(
                    nValue=0,
                    sValue=self.last_seen_text.get(mac, "Never")
                )

        anyone = len(present_names) > 0

        if UNIT_ANYONE in Devices:
            Devices[UNIT_ANYONE].Update(
                nValue=1 if anyone else 0,
                sValue="On" if anyone else "Off"
            )

        if anyone:
            status = "Home: " + ", ".join(present_names)
        else:
            status = "Nobody home"

        if UNIT_STATUS in Devices:
            Devices[UNIT_STATUS].Update(
                nValue=0,
                sValue=status[:255]
            )


_plugin = PresenceARP()

def onStart():
    _plugin.onStart()

def onHeartbeat():
    _plugin.onHeartbeat()

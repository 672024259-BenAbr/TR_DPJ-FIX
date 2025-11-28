import logging
from typing import List, Dict
from netmiko import ConnectHandler

# Logging agar terlihat prosesnya di terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkDevice:
    def __init__(self):
        self.device_config = {
            "device_type": "cisco_nxos",
            "host": "sbx-nxos-mgmt.cisco.com",
            "username": "admin",
            "password": "Admin_1234!",
            "port": 22,
            "timeout": 90,           # Timeout diperpanjang
            "global_delay_factor": 2 # Jeda diperpanjang agar tidak putus
        }

    def connect(self):
        try:
            self.connection = ConnectHandler(**self.device_config)
            return True
        except Exception as e:
            print(f"Connection Error: {e}")
            raise e

    def disconnect(self):
        if hasattr(self, 'connection'):
            self.connection.disconnect()

    def get_all_vlans(self) -> List[Dict]:
        """Mengambil data VLAN dari Router"""
        if not self.connection: return []
        try:
            # Menggunakan TextFSM (jika ada) atau parsing manual
            raw = self.connection.send_command("show vlan brief")
            vlans = []
            lines = raw.splitlines()
            for line in lines:
                parts = line.split()
                # Parsing baris yang diawali angka (Itu ID VLAN)
                if parts and parts[0].isdigit():
                    vlans.append({
                        "vlan_id": parts[0],
                        "name": parts[1],
                        "status": parts[2] if len(parts) > 2 else "active"
                    })
            return vlans
        except Exception:
            return []

    def create_vlan(self, vlan_id, vlan_name):
        """Membuat VLAN Baru"""
        try:
            cfg = [f"vlan {vlan_id}", f"name {vlan_name}", "exit"]
            self.connection.send_config_set(cfg)
            self.connection.save_config()
            return True
        except: return False

    def delete_vlan(self, vlan_id):
        """Menghapus VLAN"""
        # Jangan hapus VLAN 1 (Default)
        if vlan_id == "1": return False
        try:
            self.connection.send_config_set(f"no vlan {vlan_id}")
            self.connection.save_config()
            return True
        except: return False
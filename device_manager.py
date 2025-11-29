import logging
import time
from typing import List, Dict
from netmiko import ConnectHandler

# --- KONFIGURASI ---
# Set True untuk DEMO (Cepat & Lancar)
# Set False untuk KONEK CISCO ASLI (Butuh Internet Stabil)
USE_MOCK_MODE = True 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Palsu untuk Simulasi
MOCK_DB_VLANS = [
    {"vlan_id": "1", "name": "default", "status": "active"},
    {"vlan_id": "10", "name": "MARKETING", "status": "active"},
    {"vlan_id": "20", "name": "FINANCE", "status": "active"},
]

class NetworkDevice:
    def __init__(self):
        self.device_config = {
            "device_type": "cisco_nxos",
            "host": "sbx-nxos-mgmt.cisco.com",
            "username": "admin",
            "password": "Admin_1234!",
            "port": 22,
            "timeout": 30,           
            "global_delay_factor": 2 
        }

    def connect(self):
        if USE_MOCK_MODE:
            return True
        try:
            self.connection = ConnectHandler(**self.device_config)
            return True
        except Exception as e:
            print(f"Koneksi Gagal: {e}")
            raise e

    def disconnect(self):
        if USE_MOCK_MODE: return
        if hasattr(self, 'connection'):
            self.connection.disconnect()

    def get_all_vlans(self) -> List[Dict]:
        if USE_MOCK_MODE:
            return MOCK_DB_VLANS

        if not self.connection: return []
        try:
            raw = self.connection.send_command("show vlan brief")
            vlans = []
            lines = raw.splitlines()
            for line in lines:
                parts = line.split()
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
        if USE_MOCK_MODE:
            # Cek jika ID sudah ada (untuk simulasi update)
            for v in MOCK_DB_VLANS:
                if v['vlan_id'] == str(vlan_id):
                    v['name'] = vlan_name # Update nama
                    return True
            
            # Jika belum ada, buat baru
            MOCK_DB_VLANS.append({
                "vlan_id": str(vlan_id),
                "name": vlan_name,
                "status": "active"
            })
            return True

        # Logic Asli Netmiko
        try:
            cfg = [f"vlan {vlan_id}", f"name {vlan_name}", "exit"]
            self.connection.send_config_set(cfg)
            self.connection.save_config()
            return True
        except: return False
    
    # --- INI FUNGSI YANG HILANG TADI ---
    def update_vlan(self, vlan_id, vlan_name):
        # Panggil fungsi create_vlan karena logikanya sama (menimpa)
        return self.create_vlan(vlan_id, vlan_name)

    def delete_vlan(self, vlan_id):
        if vlan_id == "1": return False

        if USE_MOCK_MODE:
            global MOCK_DB_VLANS
            initial_len = len(MOCK_DB_VLANS)
            MOCK_DB_VLANS = [v for v in MOCK_DB_VLANS if v['vlan_id'] != str(vlan_id)]
            return True

        try:
            self.connection.send_config_set(f"no vlan {vlan_id}")
            self.connection.save_config()
            return True
        except: return False
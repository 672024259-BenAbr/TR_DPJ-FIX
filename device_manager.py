import logging
from typing import List, Dict
from netmiko import ConnectHandler

# --- KONFIGURASI UTAMA ---
# WAJIB FALSE agar data tersimpan di Cisco (Bukan di laptop)
USE_MOCK_MODE = False 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkDevice:
    def __init__(self):
        # Konfigurasi Cisco Sandbox Asli
        self.device_config = {
            "device_type": "cisco_nxos",
            "host": "sbx-nxos-mgmt.cisco.com",
            "username": "admin",
            "password": "Admin_1234!",
            "port": 22,
            "timeout": 60,           
            "global_delay_factor": 2 
        }

    def connect(self):
        # Mode Mock dihapus, kita paksa konek asli
        try:
            self.connection = ConnectHandler(**self.device_config)
            return True
        except Exception as e:
            print(f"Koneksi Cisco Gagal: {e}")
            raise e

    def disconnect(self):
        if hasattr(self, 'connection'):
            self.connection.disconnect()

    def get_all_vlans(self) -> List[Dict]:
        """Mengambil data LANGSUNG dari Router Cisco"""
        if not self.connection: return []
        try:
            # Kirim perintah asli ke router
            raw = self.connection.send_command("show vlan brief")
            vlans = []
            
            # Parsing Text Output dari Cisco
            lines = raw.splitlines()
            for line in lines:
                parts = line.split()
                # Cek apakah baris diawali angka (ID VLAN)
                if parts and parts[0].isdigit():
                    v_id = parts[0]
                    full_name = parts[1] # Contoh: "LAB__Budi__123" atau "default"
                    status = parts[2] if len(parts) > 2 else "active"
                    
                    # --- LOGIKA DECODE (MEMECAH NAMA) ---
                    # Kita cek apakah nama vlan mengandung tanda rahasia "__"
                    if "__" in full_name:
                        # Format kita: NamaVlan__NamaMhs__NIM
                        split_data = full_name.split("__")
                        real_vlan_name = split_data[0]
                        student_name = split_data[1] if len(split_data) > 1 else "-"
                        student_nim = split_data[2] if len(split_data) > 2 else "-"
                    else:
                        # Format biasa (bukan buatan aplikasi kita)
                        real_vlan_name = full_name
                        student_name = "System/Lain"
                        student_nim = "-"

                    vlans.append({
                        "vlan_id": v_id,
                        "name": real_vlan_name,
                        "status": status,
                        "student_name": student_name, # Data ini diambil dari nama vlan
                        "student_nim": student_nim    # Data ini diambil dari nama vlan
                    })
            return vlans
        except Exception as e:
            print(f"Error Get VLANs: {e}")
            return []

    def create_vlan(self, vlan_id, vlan_name, student_name="Admin", student_nim="000"):
        """Menyimpan data ke Router dengan Format Khusus"""
        
        # --- LOGIKA ENCODE (GABUNG NAMA) ---
        # Kita selipkan Nama Mhs & NIM ke dalam Nama VLAN agar tersimpan di Cisco
        # Ubah spasi jadi underscore agar tidak error di CLI Cisco
        safe_vlan = vlan_name.replace(" ", "_")
        safe_student = student_name.replace(" ", "_")
        
        # Format Akhir: LAB_JARKOM__Budi_Santoso__12345
        combined_name = f"{safe_vlan}__{safe_student}__{student_nim}"
        
        # Potong jika terlalu panjang (Cisco punya batas karakter nama vlan)
        combined_name = combined_name[:32] 

        try:
            commands = [
                f"vlan {vlan_id}",
                f"name {combined_name}", # Kirim nama yang sudah dimodifikasi
                "exit"
            ]
            output = self.connection.send_config_set(commands)
            print(f"Config Output: {output}")
            
            # WAJIB SAVE CONFIG AGAR TIDAK HILANG SAAT RESTART ROUTER
            self.connection.save_config()
            return True
        except Exception as e:
            print(f"Error Create: {e}")
            return False
    
    def update_vlan(self, vlan_id, vlan_name, student_name="Admin", student_nim="000"):
        # Di Cisco, update sama dengan create (menimpa)
        return self.create_vlan(vlan_id, vlan_name, student_name, student_nim)

    def delete_vlan(self, vlan_id):
        if vlan_id == "1": return False # Jangan hapus default
        try:
            command = f"no vlan {vlan_id}"
            self.connection.send_config_set(command)
            self.connection.save_config()
            return True
        except Exception as e:
            print(f"Error Delete: {e}")
            return False
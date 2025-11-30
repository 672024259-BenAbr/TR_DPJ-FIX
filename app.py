from flask import Flask, render_template, request, jsonify
from device_manager import NetworkDevice

app = Flask(__name__)

# --- ROUTES WEBSITE ---

@app.route('/')
def index():
    return render_template('index.html')

# --- ROUTES API (Jembatan ke Cisco) ---

@app.route('/api/vlans', methods=['GET'])
def get_vlans():
    """Mengambil data langsung dari Router Cisco"""
    device = NetworkDevice()
    try:
        device.connect()
        # Data yang kembali sudah berisi Nama & NIM (karena sudah di-decode di device_manager)
        vlans = device.get_all_vlans()
        device.disconnect()
        return jsonify({"status": "success", "data": vlans})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/vlans', methods=['POST'])
def create_vlan():
    """Membuat VLAN Baru"""
    data = request.json
    
    # Ambil data dari Frontend
    v_id = data.get('vlan_id')
    v_name = data.get('vlan_name')
    s_name = data.get('student_name')
    s_nim = data.get('student_nim')

    if not v_id or not v_name:
        return jsonify({"status": "error", "message": "ID dan Nama VLAN wajib diisi"}), 400

    device = NetworkDevice()
    try:
        device.connect()
        # Kirim 4 parameter ke device_manager untuk digabung jadi satu nama
        success = device.create_vlan(v_id, v_name, s_name, s_nim)
        device.disconnect()

        if success:
            return jsonify({"status": "success", "message": "VLAN Berhasil Dibuat!"})
        else:
            return jsonify({"status": "error", "message": "Gagal membuat VLAN di perangkat"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/vlans/<vlan_id>', methods=['PUT'])
def update_vlan(vlan_id):
    """Update VLAN (Sama dengan Create/Menimpa)"""
    data = request.json
    
    v_name = data.get('vlan_name')
    s_name = data.get('student_name')
    s_nim = data.get('student_nim')

    if not v_name:
        return jsonify({"status": "error", "message": "Nama VLAN baru wajib diisi"}), 400

    device = NetworkDevice()
    try:
        device.connect()
        # Panggil fungsi update (yang sebenarnya memanggil create ulang)
        success = device.update_vlan(vlan_id, v_name, s_name, s_nim)
        device.disconnect()
        
        if success:
            return jsonify({"status": "success", "message": "VLAN Berhasil Diupdate!"})
        return jsonify({"status": "error", "message": "Gagal update di perangkat"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/vlans/<vlan_id>', methods=['DELETE'])
def delete_vlan(vlan_id):
    """Menghapus VLAN"""
    device = NetworkDevice()
    try:
        device.connect()
        success = device.delete_vlan(vlan_id)
        device.disconnect()
        
        if success:
            return jsonify({"status": "success", "message": "VLAN Berhasil Dihapus!"})
        return jsonify({"status": "error", "message": "Gagal menghapus VLAN"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Threaded=True wajib agar tidak blocking saat banyak request
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
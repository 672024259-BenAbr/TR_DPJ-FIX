import sqlite3
from flask import Flask, render_template, request, jsonify
from device_manager import NetworkDevice

app = Flask(__name__)

# --- DATABASE SETUP (Menyimpan Nama Mahasiswa) ---
def init_db():
    with sqlite3.connect('vlan_owners.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS owners 
                     (vlan_id TEXT PRIMARY KEY, student_name TEXT, student_nim TEXT)''')
init_db()

# --- FUNGSI DATABASE HELPER ---
def save_owner(vlan_id, name, nim):
    with sqlite3.connect('vlan_owners.db') as conn:
        conn.execute("INSERT OR REPLACE INTO owners VALUES (?, ?, ?)", (vlan_id, name, nim))

def delete_owner(vlan_id):
    with sqlite3.connect('vlan_owners.db') as conn:
        conn.execute("DELETE FROM owners WHERE vlan_id=?", (vlan_id,))

def get_all_owners():
    with sqlite3.connect('vlan_owners.db') as conn:
        cursor = conn.execute("SELECT * FROM owners")
        return {row[0]: {'name': row[1], 'nim': row[2]} for row in cursor.fetchall()}

# --- ROUTES API ---

@app.route('/')
def index():
    return render_template('index.html')

# 1. READ (GET)
@app.route('/api/vlans', methods=['GET'])
def get_vlans():
    device = NetworkDevice()
    try:
        device.connect()
        cisco_vlans = device.get_all_vlans()
        device.disconnect()

        db_owners = get_all_owners()
        final_data = []
        
        for v in cisco_vlans:
            vid = v['vlan_id']
            if vid in db_owners:
                v['student_name'] = db_owners[vid]['name']
                v['student_nim'] = db_owners[vid]['nim']
            else:
                v['student_name'] = "-" 
                v['student_nim'] = "-"
            final_data.append(v)

        return jsonify({"status": "success", "data": final_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 2. CREATE (POST)
@app.route('/api/vlans', methods=['POST'])
def create_vlan():
    data = request.json
    v_id = data.get('vlan_id')
    v_name = data.get('vlan_name')
    s_name = data.get('student_name')
    s_nim = data.get('student_nim')

    if not v_id or not v_name:
        return jsonify({"status": "error", "message": "ID dan Nama harus diisi"}), 400

    device = NetworkDevice()
    try:
        device.connect()
        success = device.create_vlan(v_id, v_name)
        device.disconnect()

        if success:
            save_owner(v_id, s_name, s_nim)
            return jsonify({"status": "success", "message": "VLAN Berhasil Dibuat!"})
        else:
            return jsonify({"status": "error", "message": "Gagal di Cisco"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. UPDATE (PUT) <--- INI YANG ERROR 405 SEBELUMNYA
@app.route('/api/vlans/<vlan_id>', methods=['PUT'])
def update_vlan(vlan_id):
    data = request.json
    v_name = data.get('vlan_name')
    s_name = data.get('student_name')
    s_nim = data.get('student_nim')

    if not v_name:
        return jsonify({"status": "error", "message": "Nama VLAN baru wajib diisi"}), 400

    device = NetworkDevice()
    try:
        device.connect()
        # Di Cisco, menimpa dengan ID sama = Update
        success = device.update_vlan(vlan_id, v_name)
        device.disconnect()
        
        if success:
            save_owner(vlan_id, s_name, s_nim)
            return jsonify({"status": "success", "message": "VLAN Berhasil Diupdate!"})
        return jsonify({"status": "error", "message": "Gagal update"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 4. DELETE (DELETE)
@app.route('/api/vlans/<vlan_id>', methods=['DELETE'])
def delete_vlan(vlan_id):
    device = NetworkDevice()
    try:
        device.connect()
        success = device.delete_vlan(vlan_id)
        device.disconnect()
        
        if success:
            delete_owner(vlan_id)
            return jsonify({"status": "success", "message": "VLAN Berhasil Dihapus!"})
        return jsonify({"status": "error", "message": "Gagal menghapus"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Threaded true wajib agar tidak lemot saat banyak request
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
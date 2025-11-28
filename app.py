import sqlite3
from flask import Flask, render_template, request, jsonify
from device_manager import NetworkDevice

app = Flask(__name__)

# --- DATABASE SETUP (Menyimpan Nama Mahasiswa) ---
def init_db():
    """Membuat tabel database jika belum ada"""
    with sqlite3.connect('vlan_owners.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS owners 
                     (vlan_id TEXT PRIMARY KEY, student_name TEXT, student_nim TEXT)''')
        conn.commit()

init_db() # Jalankan saat start

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
        # Ubah jadi Dictionary biar gampang dicari: {'10': {'name': 'Budi', 'nim': '123'}}
        return {row[0]: {'name': row[1], 'nim': row[2]} for row in cursor.fetchall()}

# --- ROUTES API ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vlans', methods=['GET'])
def get_vlans():
    device = NetworkDevice()
    try:
        # 1. Ambil Data Real dari Cisco
        device.connect()
        cisco_vlans = device.get_all_vlans()
        device.disconnect()

        # 2. Ambil Data Nama dari Database Lokal
        db_owners = get_all_owners()

        # 3. GABUNGKAN (Merge) Data
        final_data = []
        for v in cisco_vlans:
            vid = v['vlan_id']
            # Cek apakah ada pemiliknya di database?
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

@app.route('/api/vlans', methods=['POST'])
def create_vlan():
    # Menerima data JSON dari Web/Postman
    data = request.json
    
    # KUNCI UTAMA: Nama variabel ini harus sama dengan yang dikirim JS/Postman
    v_id = data.get('vlan_id')
    v_name = data.get('vlan_name')
    s_name = data.get('student_name')
    s_nim = data.get('student_nim')

    if not v_id or not v_name:
        return jsonify({"status": "error", "message": "ID and Name required"}), 400

    device = NetworkDevice()
    try:
        device.connect()
        success = device.create_vlan(v_id, v_name)
        device.disconnect()

        if success:
            # Simpan Nama & NIM ke Database Lokal
            save_owner(v_id, s_name, s_nim)
            return jsonify({"status": "success", "message": "VLAN Created"})
        else:
            return jsonify({"status": "error", "message": "Failed on Cisco"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/vlans/<vlan_id>', methods=['DELETE'])
def delete_vlan(vlan_id):
    device = NetworkDevice()
    try:
        device.connect()
        success = device.delete_vlan(vlan_id)
        device.disconnect()
        
        if success:
            # Hapus juga dari database
            delete_owner(vlan_id)
            return jsonify({"status": "success", "message": "VLAN Deleted"})
        return jsonify({"status": "error", "message": "Delete Failed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # threaded=True wajib agar bisa diakses banyak laptop sekaligus
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
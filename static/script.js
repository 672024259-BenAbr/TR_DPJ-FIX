// NAVIGASI
function showScreen(name) {
    // Sembunyikan semua layar
    ['menu', 'create', 'read', 'update', 'delete', 'list'].forEach(id => {
        document.getElementById('screen-' + id).classList.add('hidden');
    });
    // Tampilkan yg dipilih
    document.getElementById('screen-' + name).classList.remove('hidden');

    if (name === 'list') fetchData();
    
    // Reset input menu
    document.getElementById('menuInput').value = '';
    // Reset Read result
    document.getElementById('readResultArea').classList.add('hidden');

    // Reset Update form visual
    document.getElementById('formUpdateArea').style.opacity = "0.3";
    document.getElementById('formUpdateArea').style.pointerEvents = "none";
    document.getElementById('searchUpdateInput').value = "";
    document.getElementById('updateName').value = "";
}

function processMenu() {
    const val = document.getElementById('menuInput').value;
    if (val === '1') showScreen('create');
    else if (val === '2') showScreen('read');
    else if (val === '3') showScreen('update');
    else if (val === '4') showScreen('delete');
    else if (val === '5') showScreen('list');
    else if (val === '6') window.close();
    else alert("Invalid Command. Select 1-6.");
}

// --- API FUNCTIONS (CRUD) ---

// 1. CREATE
async function actionCreate() {
    const id = document.getElementById('createId').value;
    const name = document.getElementById('createName').value;
    const user = document.getElementById('globalName').value;
    if (!id || !name) return alert("Error: Missing Parameters!");
    
    try {
        const res = await fetch('/api/vlans', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ vlan_id: id, vlan_name: name, student_name: user, student_nim: "000" })
        });
        const json = await res.json();
        alert("System: " + json.message);
        if (json.status === 'success') showScreen('menu');
    } catch (e) { 
        console.log(e);
        alert("Connection Failed. Check Console."); 
    }
}

// 2. READ (SEARCH SINGLE)
async function actionSearchRead() {
    const idCari = document.getElementById('searchReadInput').value;
    if (!idCari) return alert("Input ID required!");

    try {
        const res = await fetch('/api/vlans');
        const json = await res.json();
        
        // Filter client-side
        const found = json.data.find(v => v.vlan_id == idCari);

        if (found) {
            document.getElementById('readResultArea').classList.remove('hidden');
            document.getElementById('resId').innerText = found.vlan_id;
            document.getElementById('resName').innerText = found.name;
            document.getElementById('resUser').innerText = found.student_name;
        } else {
            document.getElementById('readResultArea').classList.add('hidden');
            alert("VLAN ID " + idCari + " Not Found in Database.");
        }
    } catch (e) { alert("Data Fetch Error"); }
}

// 3. UPDATE - Search before update
async function cariUntukUpdate() {
    const idCari = document.getElementById('searchUpdateInput').value;
    if (!idCari) return alert("Input ID required!");
    try {
        const res = await fetch('/api/vlans');
        const json = await res.json();
        const found = json.data.find(v => v.vlan_id == idCari);
        if (found) {
            const formArea = document.getElementById('formUpdateArea');
            formArea.style.opacity = "1";
            formArea.style.pointerEvents = "auto";
            
            document.getElementById('updateId').value = found.vlan_id;
            document.getElementById('updateName').value = found.name;
            document.getElementById('updateName').focus();
        } else {
            alert("ID Not Found.");
        }
    } catch (e) { alert("Connection Error"); }
}

async function actionUpdate() {
    const id = document.getElementById('updateId').value;
    const name = document.getElementById('updateName').value;
    const user = document.getElementById('globalName').value;
    try {
        const res = await fetch(`/api/vlans/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ vlan_name: name, student_name: user, student_nim: "000" })
        });
        const json = await res.json();
        alert(json.message);
        if (json.status === 'success') showScreen('menu');
    } catch (e) { alert("Update Failed"); }
}

// 4. DELETE
async function actionDelete() {
    const id = document.getElementById('deleteId').value;
    if (!confirm("WARNING: Are you sure you want to delete VLAN " + id + "?")) return;
    try {
        const res = await fetch(`/api/vlans/${id}`, { method: 'DELETE' });
        const json = await res.json();
        alert(json.message);
        if (json.status === 'success') showScreen('menu');
    } catch (e) { alert("Delete Failed"); }
}

// 5. SHOW ALL
async function fetchData() {
    const box = document.getElementById('listContainer');
    box.innerHTML = '<div style="text-align:center; padding:20px; color:#0ea5e9;">Scanning Network...</div>';
    try {
        const res = await fetch('/api/vlans');
        const json = await res.json();
        if (!json.data || json.data.length === 0) { 
            box.innerHTML = '<div style="text-align:center; color:#64748b; padding:20px;">No Data Available.</div>'; 
            return; 
        }
        
        let html = '';
        json.data.forEach(v => {
            html += `
            <div class="list-item">
                <div>
                    <span class="badge-id">ID: ${v.vlan_id}</span>
                    <span style="margin-left:10px; font-weight:600; color:#f1f5f9;">${v.name}</span>
                </div>
                <small style="color:#94a3b8;">${v.student_name}</small>
            </div>`;
        });
        box.innerHTML = html;
    } catch (e) { 
        box.innerHTML = '<div style="text-align:center; color:#ef4444; padding:20px;">Connection Lost.</div>'; 
    }
}
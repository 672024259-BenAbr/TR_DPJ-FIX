const API_URL = '/api/vlans';


const teamData = {
    
    "Brillian": { nim: "672024246", tugas: "Frontend UI" },
    "Brillian Kusuma": { nim: "672024246", tugas: "Frontend UI" },
    
    "Talita":   { nim: "672024251", tugas: "Frontend UI" },
    "Talita Dian": { nim: "672024251", tugas: "Frontend UI" },
    
    "Khulud":   { nim: "672024253", tugas: "Frontend UI, flow" },
    "Khulud Zuliyani": { nim: "672024253", tugas: "frontend UI, flow" },
    
    "Berlian":  { nim: "672024254", tugas: "Backend" },
    "Berlian Rezin": { nim: "672024254", tugas: "Backend" },
    
    "Benri":    { nim: "672024259", tugas: "Backend" },
    "Benri Abrian": { nim: "672024259", tugas: "Backend" },

    "Admin":    { nim: "-", tugas: "-" }
};

function showScreen(screenName) {
    const screens = document.querySelectorAll('.sub-screen, .card-menu');
    screens.forEach(s => s.classList.add('hidden'));

    if (screenName === 'menu') {
        document.getElementById('screen-menu').classList.remove('hidden');
        document.getElementById('menuInput').value = '';
    } else {
        document.getElementById('screen-' + screenName).classList.remove('hidden');
    }
}

function processMenu() {
    const choice = document.getElementById('menuInput').value;
    const map = {
        '1': 'create', '2': 'read', '3': 'update', 
        '4': 'delete', '5': 'list', '6': 'exit'
    };

    if(choice === '6') {
        alert("SYSTEM TERMINATED.");
        window.location.reload();
    } else if (map[choice]) {
        showScreen(map[choice]);
        if(map[choice] === 'list') fetchData();
    } else {
        alert("ACCESS DENIED: Select 1-6");
    }
}

function actionCreate() {
    const id = document.getElementById('createId').value;
    const name = document.getElementById('createName').value;
    
    const inputUser = document.getElementById('globalName').value;
    const user = inputUser && inputUser.trim() !== "" ? inputUser : "Admin";

    if(!id || !name) return alert("ERROR: Missing ID or LABEL!");

    fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            vlan_id: id, 
            vlan_name: name,
            student_name: user,   
            student_nim: "00000"  
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if(data.status === 'success') {
            document.getElementById('createId').value = '';
            document.getElementById('createName').value = '';
            showScreen('menu');
        }
    })
    .catch(() => alert("CONNECTION FAILURE"));
}

function actionSearchRead() {
    const id = document.getElementById('searchReadInput').value;
    const resultArea = document.getElementById('readResultArea');

    if(!id) return alert("INPUT REQUIRED");

    fetch(API_URL)
    .then(res => res.json())
    .then(json => {
        const found = json.data.find(v => v.vlan_id == id);
        if(found) {
            resultArea.classList.remove('hidden');
            document.getElementById('resId').innerText = found.vlan_id;
            document.getElementById('resName').innerText = found.name;
            document.getElementById('resUser').innerText = found.student_name;
        } else {
            alert("TARGET NOT FOUND");
            resultArea.classList.add('hidden');
        }
    });
}

function cariUntukUpdate() {
    const id = document.getElementById('searchUpdateInput').value;
    const formArea = document.getElementById('formUpdateArea');

    if(!id) return alert("INPUT TARGET ID");

    fetch(API_URL)
    .then(res => res.json())
    .then(json => {
        const found = json.data.find(v => v.vlan_id == id);
        if(found) {
            formArea.style.opacity = "1";
            formArea.style.pointerEvents = "all";
            document.getElementById('updateName').value = found.name;
            document.getElementById('updateId').value = found.vlan_id; 
        } else {
            alert("TARGET NOT FOUND");
            formArea.style.opacity = "0.3";
            formArea.style.pointerEvents = "none";
        }
    });
}

function actionUpdate() {
    const id = document.getElementById('updateId').value;
    const name = document.getElementById('updateName').value;
    const inputUser = document.getElementById('globalName').value;
    const user = inputUser && inputUser.trim() !== "" ? inputUser : "Admin";

    fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            vlan_name: name, student_name: user, student_nim: "00000"
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if(data.status === 'success') showScreen('menu');
    });
}

function actionDelete() {
    const id = document.getElementById('deleteId').value;
    if(!id) return alert("INPUT REQUIRED");
    if(!confirm(`Delete VLAN ${id}?`)) return;

    fetch(`${API_URL}/${id}`, { method: 'DELETE' })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if(data.status === 'success') {
            document.getElementById('deleteId').value = '';
            showScreen('menu');
        }
    });
}

function fetchData() {
    const container = document.getElementById('listContainer');
    container.innerHTML = '<div style="text-align:center; color:#94a3b8;">Scanning Matrix...</div>';

    fetch(API_URL)
    .then(res => res.json())
    .then(json => {
        container.innerHTML = ''; 
        if(!json.data || json.data.length === 0) {
            container.innerHTML = '<div style="text-align:center;">No Active VLANs.</div>';
            return;
        }

        let html = '<table class="result-table" style="width:100%; text-align:left;">';
        html += `
        <tr style="border-bottom:1px solid #444; color:var(--primary);">
            <th>ID</th>
            <th>VLAN NAME</th>
            <th>MEMBER NAME</th>
            <th>JOBDESK</th>
        </tr>`;
        
        json.data.forEach((vlan) => {
            
            let creatorName = vlan.student_name; 
            
            let info = teamData[creatorName] || { nim: "-", tugas: "Guest / External" };

            html += `
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                <td style="padding:10px; color:var(--accent); font-weight:bold;">${vlan.vlan_id}</td>
                <td style="padding:10px;">${vlan.name}</td>
                
                <td style="padding:10px;">
                    <span style="color:#e2e8f0; font-weight:bold;">${creatorName}</span><br>
                    <span style="font-size:11px; color:#64748b;">${info.nim}</span>
                </td> 
                
                <td style="padding:10px;">
                    <span class="task-badge">${info.tugas}</span>
                </td>
            </tr>`;
        });
        html += '</table>';
        container.innerHTML = html;
    })
    .catch(() => {
        container.innerHTML = '<div style="text-align:center; color:#ef4444;">LINK FAILED</div>';
    });
}
const API_BASE = "http://localhost:8000/api";
let currentBuilding = null;
let allBuildings = [];
let limit = 24; 
let notifiedAlerts = new Set();
let cRealtime, cXai, cTemp, cWind, cProfile;

// TỪ ĐIỂN DỊCH THUẬT AI SANG NGÔN NGỮ NGƯỜI QUẢN LÝ
const dictFeature = {
    'airTemperature': { name: 'Nhiệt độ ngoài trời', advice: 'Nhiệt độ môi trường gây áp lực lên hệ thống. Đề nghị kiểm tra công suất Hệ thống Điều hòa (HVAC), đóng rèm che nắng.' },
    'dewTemperature': { name: 'Độ ẩm không khí', advice: 'Độ ẩm quá cao làm giảm hiệu suất trao đổi nhiệt. Hãy rà soát lại hệ thống thông gió và dàn ngưng tụ.' },
    'windSpeed': { name: 'Tốc độ gió', advice: 'Gió mạnh có khả năng làm thất thoát nhiệt độ trong nhà. Kiểm tra lại độ kín của các cửa sổ.' },
    'seaLvlPressure': { name: 'Áp suất khí quyển', advice: 'Áp suất thay đổi báo hiệu thời tiết cực đoan, chuẩn bị sẵn sàng phương án điện dự phòng.' },
    'enthalpy': { name: 'Chỉ số nhiệt ẩm (Enthalpy)', advice: 'Không khí mang lượng nhiệt lớn. Yêu cầu bộ phận Kỹ thuật kiểm tra ngay hiệu suất Chiller.' },
    'load_lag_1': { name: 'Mức tải 1 giờ trước', advice: 'Có thiết bị công suất lớn vừa được bật lên hoặc bị kẹt. Cần đi tuần tra thực tế ngay lập tức.' },
    'load_lag_2': { name: 'Mức tải 2 giờ trước', advice: 'Tình trạng tải bất thường đã duy trì liên tục 2 tiếng đồng hồ. Kiểm tra lịch trình vận hành thiết bị.' },
    'load_lag_24': { name: 'Mức tải cùng giờ hôm qua', advice: 'Hôm nay tiêu thụ đột biến so với thói quen hôm qua. Có sự kiện đặc biệt hoặc quên tắt máy móc?' },
    'load_diff_1': { name: 'Tốc độ thay đổi tải (1h)', advice: 'Hệ thống điện bị sốc tải do đóng ngắt thiết bị đột ngột. Rà soát bảng điện trung tâm.' },
    'roll_mean_24h': { name: 'Trung bình tải 24h', advice: 'Mặt bằng tiêu thụ chung cả ngày hôm nay đang bị lệch. Báo cáo quản lý tòa nhà.' }
};
function translate(key) { return dictFeature[key] || { name: key, advice: 'Vui lòng kiểm tra tình trạng vận hành thiết bị liên quan đến thông số này.' }; }

function initCharts() {
    cRealtime = new Chart(document.getElementById('realtimeChart'), { type: 'line', data: { labels: [], datasets: [ { label: 'Thực tế', borderColor: '#0f172a', borderWidth: 2, data: [], pointRadius: 0, z: 10 }, { label: 'Dự báo', borderColor: '#3b82f6', borderDash: [5, 5], borderWidth: 2, data: [], pointRadius: 0 }, { label: 'Sự cố', backgroundColor: '#ef4444', pointStyle: 'circle', pointRadius: 6, data: [], type: 'scatter' }, { label: 'Ngưỡng', data: [], borderColor: 'transparent', fill: false, pointRadius: 0 }, { label: 'An Toàn', data: [], borderColor: 'transparent', backgroundColor: 'rgba(16, 185, 129, 0.15)', fill: '-1', pointRadius: 0 } ]}, options: { responsive: true, maintainAspectRatio: false, animation: false }});
    cXai = new Chart(document.getElementById('xaiChart'), { type: 'bar', data: { labels: [], datasets: [{ label: '% Tác động', backgroundColor: '#ef4444', data: [] }] }, options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y' } });
    cTemp = new Chart(document.getElementById('tempChart'), { type: 'line', data: { labels: [], datasets: [{ label: 'Nhiệt độ', borderColor: '#ef4444', data: [], pointRadius:0 }, { label: 'Độ ẩm', borderColor: '#38bdf8', data: [], pointRadius:0 }] }, options: { responsive: true, maintainAspectRatio: false, animation: false } });
    cWind = new Chart(document.getElementById('windChart'), { type: 'line', data: { labels: [], datasets: [{ label: 'Gió', borderColor: '#8b5cf6', data: [], pointRadius:0, yAxisID: 'y1' }, { label: 'Áp suất', borderColor: '#64748b', data: [], borderDash: [2,2], pointRadius:0, yAxisID: 'y2' }] }, options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { y1: {position: 'left'}, y2: {position: 'right', grid:{drawOnChartArea:false}} } } });
    cProfile = new Chart(document.getElementById('profileChart'), { type: 'bar', data: { labels: [], datasets: [{ label: 'Tải', backgroundColor: '#10b981', data: [] }] }, options: { responsive: true, maintainAspectRatio: false } });
}

function renderSidebar(filter = "") {
    const list = document.getElementById('building-list'); list.innerHTML = '';
    allBuildings.filter(b => b.toLowerCase().includes(filter.toLowerCase())).forEach(b => {
        const item = document.createElement('div'); item.className = `b-item ${b === currentBuilding ? 'active' : ''}`; item.innerText = b;
        item.onclick = () => { currentBuilding = b; document.getElementById('building-title').innerText = b; renderSidebar(document.getElementById('search-input').value); fetchHistoricalData(); };
        list.appendChild(item);
    });
}

async function fetchGlobalAlerts() {
    try {
        const alerts = await (await fetch(`${API_BASE}/alerts/global`)).json();
        const listDiv = document.getElementById('alerts-list'); const badge = document.getElementById('alert-badge'); const bellIcon = document.getElementById('bell-icon');
        let newCount = 0; listDiv.innerHTML = '';
        alerts.forEach(a => {
            const id = `${a.timestamp}-${a.building}`;
            if(!notifiedAlerts.has(id)) { notifiedAlerts.add(id); newCount++; }
            const el = document.createElement('div'); el.className = 'alert-item';
            el.innerHTML = `<div class="alert-title"><span style="color: var(--danger)">🚨 ${a.building}</span> <span style="font-size:11px;color:#64748b">${a.timestamp.split(" ")[1]}</span></div><div class="alert-desc">Phát hiện tải bất thường: ${a.load.toFixed(1)} kWh</div>`;
            el.onclick = () => { currentBuilding = a.building; document.getElementById('alerts-panel').classList.remove('show'); renderSidebar(); };
            listDiv.appendChild(el); // Fix Bug appendChild ở đây
        });
        if(newCount > 0) { badge.innerText = newCount; badge.classList.remove('hidden'); bellIcon.classList.add('ringing'); setTimeout(() => bellIcon.classList.remove('ringing'), 1000); } 
        else if(alerts.length === 0) listDiv.innerHTML = `<div style="padding:20px;text-align:center;color:#94a3b8;font-size:12px;">Hệ thống an toàn.</div>`;
    } catch(e) {}
}

async function fetchHistoricalData() {
    if(!currentBuilding) return;
    try {
        const data = await (await fetch(`${API_BASE}/analytics/hourly_profile?building_name=${currentBuilding}`)).json();
        cProfile.data.labels = data.map(d => d.hour); cProfile.data.datasets[0].data = data.map(d => d.avg_load); cProfile.update();
    } catch(e) {}
}

async function fetchRealtimeLoop() {
    if(allBuildings.length === 0) {
        try {
            allBuildings = await (await fetch(`${API_BASE}/buildings`)).json();
            if(allBuildings.length > 0) { currentBuilding = allBuildings[0]; document.getElementById('building-title').innerText = currentBuilding; fetchHistoricalData(); }
            renderSidebar();
        } catch(e) { return; }
    }
    if(!currentBuilding) return;

    try {
        const data = await (await fetch(`${API_BASE}/data?building_name=${currentBuilding}&limit=${limit}`)).json();
        if(data.length > 0) {
            const lb = [], ac = [], pr = [], an = [], up = [], lw = [];
            data.forEach(d => { lb.push(d.timestamp.split(" ")[1]); ac.push(d.actual_load); pr.push(d.predicted_load); an.push(d.is_anomaly ? d.actual_load : null); up.push(d.predicted_load + d.threshold); lw.push(d.predicted_load - d.threshold); });
            cRealtime.data.labels = lb; cRealtime.data.datasets[0].data = ac; cRealtime.data.datasets[1].data = pr; cRealtime.data.datasets[2].data = an; cRealtime.data.datasets[3].data = lw; cRealtime.data.datasets[4].data = up; cRealtime.update();
            
            const last = data[data.length - 1];
            document.getElementById('time-display').innerText = `Cập nhật lúc: ${last.timestamp}`;
            document.getElementById('kpi-cur').innerText = last.actual_load.toFixed(1);
            
            // INSIGHT REALTIME
            const trend = (ac.length>1 && ac[ac.length-1] > ac[ac.length-2]) ? "đang tăng" : "đang giảm";
            const diff = Math.abs(last.predicted_load + last.threshold - last.actual_load).toFixed(1);
            if(last.is_anomaly) document.getElementById('insight-realtime').innerHTML = `⚠️ <b>Hệ thống đang rủi ro!</b> Tải ${trend} vượt ngưỡng dự báo an toàn. Yêu cầu kiểm tra ngay XAI.`;
            else document.getElementById('insight-realtime').innerHTML = `✅ Hệ thống ổn định. Tải tiêu thụ ${trend} hợp lý. Mức điện cách ngưỡng rủi ro <b>${diff} kWh</b>.`;
        }

        const s = await (await fetch(`${API_BASE}/stats/summary?building_name=${currentBuilding}`)).json();
        document.getElementById('kpi-sum').innerText = s.sum.toFixed(1); document.getElementById('kpi-max').innerText = s.max.toFixed(1); document.getElementById('kpi-min').innerText = s.min.toFixed(1);

        const x = await (await fetch(`${API_BASE}/explain?building_name=${currentBuilding}`)).json();
        const xText = document.getElementById('insight-xai');
        if(x.explanation) {
            const featuresRaw = Object.keys(x.explanation);
            const humanLabels = featuresRaw.map(k => translate(k).name);
            cXai.data.labels = humanLabels; cXai.data.datasets[0].data = Object.values(x.explanation); cXai.update(); 
            xText.innerHTML = `Lỗi gần nhất lúc <b>${x.timestamp}</b>.<br>Xem chi tiết Nguyên nhân và Cách xử lý trong mục <b>Lịch sử</b>.`;
            xText.style.background = "#fff1f2"; xText.style.color = "#991b1b";
        } else {
            cXai.data.labels = []; cXai.data.datasets[0].data = []; cXai.update();
            xText.innerHTML = `Không có sự cố nào được ghi nhận. Hệ thống an toàn.`;
            xText.style.background = "#f8fafc"; xText.style.color = "#64748b";
        }

        const wData = await (await fetch(`${API_BASE}/weather/correlation?building_name=${currentBuilding}&limit=168`)).json();
        cTemp.data.labels = wData.map(w => w.time); cTemp.data.datasets[0].data = wData.map(w => w.temp); cTemp.data.datasets[1].data = wData.map(w => w.dew); cTemp.update();
        cWind.data.labels = wData.map(w => w.time); cWind.data.datasets[0].data = wData.map(w => w.wind); cWind.data.datasets[1].data = wData.map(w => w.pressure); cWind.update();
        
        // INSIGHT WEATHER
        if(wData.length > 0) {
            const currTemp = wData[wData.length-1].temp;
            if(currTemp > 25) document.getElementById('insight-temp').innerHTML = `🔥 Nhiệt độ đang cao (<b>${currTemp}°C</b>), nguy cơ làm tăng tải điều hòa (Chiller) của tòa nhà.`;
            else document.getElementById('insight-temp').innerHTML = `🌤️ Nhiệt độ mát mẻ (<b>${currTemp}°C</b>), thời tiết đang hỗ trợ tốt cho việc tiết kiệm điện năng.`;
        }

    } catch(e) {}
}

// ================= MODAL LỊCH SỬ & SNAPSHOT =================
async function openHistoryModal() {
    if(!currentBuilding) return;
    document.getElementById('modal-title').innerText = `Lịch sử Cảnh báo - ${currentBuilding}`;
    const modal = document.getElementById('history-modal');
    const body = document.getElementById('modal-body');
    modal.classList.add('show');
    body.innerHTML = 'Đang tải lịch sử...';
    
    try {
        const history = await (await fetch(`${API_BASE}/alerts/history?building_name=${currentBuilding}`)).json();
        if(history.length === 0) { body.innerHTML = '<i>Không có bất thường nào trong quá khứ.</i>'; return; }
        
        let html = `<table class="history-table"><thead><tr><th>Thời gian</th><th>Tải Thực tế</th><th>Dự báo AI</th><th>Trạng thái</th></tr></thead><tbody>`;
        history.forEach((h, idx) => {
            html += `<tr onclick="showSnapshot(${idx})"><td>${h.timestamp}</td><td><b>${h.actual_load.toFixed(1)} kWh</b></td><td>${h.predicted_load.toFixed(1)} kWh</td><td style="color:#dc2626; font-weight:bold;">Vượt ngưỡng</td></tr>`;
        });
        html += `</tbody></table>`;
        body.innerHTML = html;
        window.currentHistoryData = history; // Cache để render Snapshot
    } catch(e) { body.innerHTML = 'Lỗi lấy dữ liệu.'; }
}

window.showSnapshot = function(idx) {
    const data = window.currentHistoryData[idx];
    let actionHtml = '';
    
    // Dịch thuật XAI
    if(data.explanation) {
        Object.keys(data.explanation).forEach(key => {
            const dict = translate(key);
            const val = data.explanation[key];
            actionHtml += `
                <div class="action-card">
                    <div class="action-title">🔴 ${dict.name} (Độ lệch: ${val}%)</div>
                    <div class="action-advice"><b>Biện pháp:</b> ${dict.advice}</div>
                </div>`;
        });
    }

    const html = `
        <button style="margin-bottom: 15px; padding: 6px 12px; cursor: pointer;" onclick="openHistoryModal()">⬅ Quay lại danh sách</button>
        <div class="snapshot-grid">
            <div class="snap-params">
                <h3 style="margin-top:0;">Trạng thái Tòa nhà (Snapshot)</h3>
                <div class="param-item"><span>Thời điểm:</span> <b>${data.timestamp}</b></div>
                <div class="param-item"><span>Tải thực tế bị sốc:</span> <b style="color:var(--danger)">${data.actual_load.toFixed(1)} kWh</b></div>
                <div class="param-item"><span>Mức tải AI kỳ vọng:</span> <b>${data.predicted_load.toFixed(1)} kWh</b></div>
                <hr style="border-top:1px solid #cbd5e1; margin: 15px 0;">
                <div class="param-item"><span>🌡️ Nhiệt độ:</span> <b>${data.temp}°C</b></div>
                <div class="param-item"><span>💧 Độ ẩm sương:</span> <b>${data.dew}°C</b></div>
                <div class="param-item"><span>🌪️ Tốc độ gió:</span> <b>${data.wind} m/s</b></div>
            </div>
            <div class="snap-actions">
                <h3 style="margin-top:0;">TOP Nguyên nhân & Kế hoạch hành động</h3>
                ${actionHtml || '<i>Không có đủ dữ liệu để phân tích nguyên nhân.</i>'}
            </div>
        </div>
    `;
    document.getElementById('modal-body').innerHTML = html;
}

// --- SỰ KIỆN ---
window.onload = () => {
    initCharts();
    document.querySelectorAll('.btn-time').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.btn-time').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active'); limit = parseInt(e.target.getAttribute('data-val')); fetchRealtimeLoop();
        });
    });
    document.getElementById('search-input').addEventListener('input', (e) => renderSidebar(e.target.value));
    const bell = document.getElementById('bell-btn'); const panel = document.getElementById('alerts-panel');
    bell.addEventListener('click', (e) => { panel.classList.toggle('show'); document.getElementById('alert-badge').classList.add('hidden'); });
    document.getElementById('btn-clear').addEventListener('click', (e) => { e.stopPropagation(); notifiedAlerts.clear(); document.getElementById('alerts-list').innerHTML = ''; document.getElementById('alert-badge').classList.add('hidden'); });
    
    // Modal
    document.getElementById('btn-show-history').addEventListener('click', openHistoryModal);
    document.getElementById('btn-close-modal').addEventListener('click', () => document.getElementById('history-modal').classList.remove('show'));

    setInterval(fetchRealtimeLoop, 500);
    setInterval(fetchGlobalAlerts, 2000);
};
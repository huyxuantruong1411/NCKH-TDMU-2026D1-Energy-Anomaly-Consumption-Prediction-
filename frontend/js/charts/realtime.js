export function initRealtimeChart() {
    const ctx = document.getElementById('realtimeChart').getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'Thực tế (Actual)', borderColor: '#1e293b', borderWidth: 2, data: [], pointRadius: 0, z: 10 },
                { label: 'Dự báo (AI)', borderColor: '#3b82f6', borderDash: [5, 5], borderWidth: 2, data: [], pointRadius: 0 },
                { label: 'Sự cố!', backgroundColor: '#ef4444', pointStyle: 'circle', pointRadius: 6, data: [], type: 'scatter' },
                { label: 'Ngưỡng dưới', data: [], borderColor: 'transparent', fill: false, pointRadius: 0 },
                { label: 'Vùng An Toàn', data: [], borderColor: 'transparent', backgroundColor: 'rgba(16, 185, 129, 0.15)', fill: '-1', pointRadius: 0 }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { y: { suggestedMin: 0 } } }
    });
}
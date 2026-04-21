export function initScatterChart() {
    const ctx = document.getElementById('scatterChart').getContext('2d');
    return new Chart(ctx, {
        type: 'scatter',
        data: { datasets: [{ label: 'Tương quan Nhiệt độ - Điện', backgroundColor: 'rgba(59, 130, 246, 0.6)', data: [] }] },
        options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { x: { title: { display: true, text: 'Nhiệt độ (°C)' } }, y: { title: { display: true, text: 'Tải (kWh)' } } } }
    });
}
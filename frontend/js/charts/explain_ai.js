export function initXaiChart() {
    const ctx = document.getElementById('xaiChart').getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: '% Biến động bất thường', backgroundColor: '#ef4444', data: [] }] },
        options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', scales: { x: { beginAtZero: true } } }
    });
}
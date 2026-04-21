export function updateKPICards(stats, currentData) {
    if(stats) {
        document.getElementById('kpi-sum').innerHTML = `${stats.sum.toFixed(1)} <small>kWh</small>`;
        document.getElementById('kpi-max').innerHTML = `${stats.max.toFixed(2)} <small>kWh</small>`;
        document.getElementById('kpi-min').innerHTML = `${stats.min.toFixed(2)} <small>kWh</small>`;
    }
    if(currentData) {
        document.getElementById('kpi-current').innerHTML = `${currentData.actual_load.toFixed(2)} <small>kWh</small>`;
    }
}
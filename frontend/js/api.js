const API_BASE = "http://localhost:8000/api";

export async function fetchBuildings() {
    const res = await fetch(`${API_BASE}/buildings`);
    return res.json();
}

export async function fetchRealtimeData(building) {
    const res = await fetch(`${API_BASE}/data?building_name=${building}&limit=100`);
    return res.json();
}

export async function fetchStats(building) {
    const res = await fetch(`${API_BASE}/stats/summary?building_name=${building}`);
    return res.json();
}

export async function fetchWeather(building) {
    const res = await fetch(`${API_BASE}/weather/correlation?building_name=${building}`);
    return res.json();
}

export async function fetchExplain(building) {
    const res = await fetch(`${API_BASE}/explain?building_name=${building}`);
    return res.json();
}
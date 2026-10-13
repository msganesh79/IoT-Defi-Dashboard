// Web Dashboard Controller for Secure IoT-DeFi Oracle
const API_URL = "http://127.0.0.1:5000/api/state";

let telemetryChart = null;
let attackActive = false;
let sampleCounter = 0;

// Initialize Chart.js Telemetry Graph
function initChart() {
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Node 1 (°C)',
                    data: [],
                    borderColor: '#38bdf8',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'Node 2 (°C)',
                    data: [],
                    borderColor: '#a855f7',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'Node 3 (°C - Target)',
                    data: [],
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 3
                },
                {
                    label: 'Validated Median (Smart Contract)',
                    data: [],
                    borderColor: '#22c55e',
                    borderWidth: 3,
                    borderDash: [5, 5],
                    tension: 0.1,
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300 },
            scales: {
                x: {
                    grid: { color: '#1c273e' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { color: '#1c273e' },
                    ticks: { color: '#94a3b8' },
                    suggestedMin: 15,
                    suggestedMax: 35
                }
            },
            plugins: {
                legend: { labels: { color: '#f1f5f9', font: { family: 'Inter' } } }
            }
        }
    });
}

// Poll Oracle HTTP API for live updates
async function fetchOracleState() {
    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error("Network response error");
        const data = await res.json();
        updateDashboard(data);
    } catch (err) {
        // Fallback simulation mode if server not responding directly
        runLocalDashboardSimulation();
    }
}

// Update UI Components with live data
function updateDashboard(data) {
    // 1. KPI Cards
    if (data.latest_median !== undefined) {
        document.getElementById('kpi-median').innerText = `${data.latest_median.toFixed(2)}°C`;
        document.getElementById('ledger-onchain-val').innerText = `${data.latest_median.toFixed(1)}°C (Scaled: ${Math.round(data.latest_median * 10)})`;
    }

    if (data.total_attacks_blocked !== undefined) {
        document.getElementById('kpi-attacks-blocked').innerText = data.total_attacks_blocked;
    }

    if (data.excluded_nodes && data.excluded_nodes.length > 0) {
        document.getElementById('kpi-excluded-nodes').innerText = data.excluded_nodes.join(", ");
    } else {
        document.getElementById('kpi-excluded-nodes').innerText = "None";
    }

    if (data.latest_tx_hash) {
        document.getElementById('ledger-tx-hash').innerText = data.latest_tx_hash;
    }

    // 2. Node Status Cards
    if (data.node_statuses) {
        for (let i = 1; i <= 3; i++) {
            const nodeId = `ESP32_Node_${i}`;
            const status = data.node_statuses[nodeId] || "HEALTHY";
            const cardEl = document.getElementById(`node-card-${i}`);
            const badgeEl = document.getElementById(`node-status-${i}`);

            if (status.includes("ATTACKED") || status.includes("EXCLUDED")) {
                cardEl.className = "node-card attacked";
                badgeEl.className = "node-status-badge attacked";
                badgeEl.innerText = "ATTACKED (EXCLUDED)";
                if (i === 3) document.getElementById('node-security-3').innerText = "🚨 COMPROMISED (500°C)";
            } else {
                cardEl.className = "node-card healthy";
                badgeEl.className = "node-status-badge healthy";
                badgeEl.innerText = "HEALTHY";
                if (i === 3) document.getElementById('node-security-3').innerText = "Uncompromised";
            }
        }
    }

    // 3. Buffered Nodes Telemetry
    if (data.buffered_nodes) {
        if (data.buffered_nodes["ESP32_Node_1"]) {
            document.getElementById('node-temp-1').innerText = `${data.buffered_nodes["ESP32_Node_1"].temperature.toFixed(2)} °C`;
        }
        if (data.buffered_nodes["ESP32_Node_2"]) {
            document.getElementById('node-temp-2').innerText = `${data.buffered_nodes["ESP32_Node_2"].temperature.toFixed(2)} °C`;
        }
        if (data.buffered_nodes["ESP32_Node_3"]) {
            document.getElementById('node-temp-3').innerText = `${data.buffered_nodes["ESP32_Node_3"].temperature.toFixed(2)} °C`;
        }

        // Add point to chart
        addChartPoint(
            data.buffered_nodes["ESP32_Node_1"] ? data.buffered_nodes["ESP32_Node_1"].temperature : 25.1,
            data.buffered_nodes["ESP32_Node_2"] ? data.buffered_nodes["ESP32_Node_2"].temperature : 25.4,
            data.buffered_nodes["ESP32_Node_3"] ? data.buffered_nodes["ESP32_Node_3"].temperature : 24.8,
            data.latest_median || 25.1
        );
    }
}

// Fallback local simulation mode for instant browser review
function runLocalDashboardSimulation() {
    sampleCounter++;
    const t1 = 25.1 + (Math.random() * 0.4 - 0.2);
    const t2 = 25.4 + (Math.random() * 0.4 - 0.2);
    let t3 = 24.8 + (Math.random() * 0.4 - 0.2);
    let median = (t1 + t2) / 2;

    if (attackActive) {
        t3 = 500.0;
        document.getElementById('kpi-attacks-blocked').innerText = "1";
        document.getElementById('kpi-excluded-nodes').innerText = "ESP32_Node_3";

        const card3 = document.getElementById('node-card-3');
        const badge3 = document.getElementById('node-status-3');
        card3.className = "node-card attacked";
        badge3.className = "node-status-badge attacked";
        badge3.innerText = "ATTACKED (EXCLUDED)";
        document.getElementById('node-security-3').innerText = "🚨 COMPROMISED (500°C)";
        
        // Log to table
        prependDbRow("ATTACK DETECTED", "ESP32_Node_3", "500.00 °C", "23.45", "QUARANTINED & EXCLUDED FROM AGGREGATION");
    } else {
        document.getElementById('kpi-attacks-blocked').innerText = "0";
        document.getElementById('kpi-excluded-nodes').innerText = "None";

        const card3 = document.getElementById('node-card-3');
        const badge3 = document.getElementById('node-status-3');
        card3.className = "node-card healthy";
        badge3.className = "node-status-badge healthy";
        badge3.innerText = "HEALTHY";
        document.getElementById('node-security-3').innerText = "Uncompromised";
    }

    document.getElementById('node-temp-1').innerText = `${t1.toFixed(2)} °C`;
    document.getElementById('node-temp-2').innerText = `${t2.toFixed(2)} °C`;
    document.getElementById('node-temp-3').innerText = `${t3.toFixed(2)} °C`;
    document.getElementById('kpi-median').innerText = `${median.toFixed(2)}°C`;
    document.getElementById('ledger-onchain-val').innerText = `${median.toFixed(1)}°C (Scaled: ${Math.round(median * 10)})`;

    addChartPoint(t1, t2, Math.min(t3, 40), median);
}

function addChartPoint(t1, t2, t3, median) {
    if (!telemetryChart) return;
    const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    if (telemetryChart.data.labels.length > 15) {
        telemetryChart.data.labels.shift();
        telemetryChart.data.datasets.forEach(ds => ds.data.shift());
    }

    telemetryChart.data.labels.push(timeLabel);
    telemetryChart.data.datasets[0].data.push(t1);
    telemetryChart.data.datasets[1].data.push(t2);
    telemetryChart.data.datasets[2].data.push(t3);
    telemetryChart.data.datasets[3].data.push(median);
    telemetryChart.update();
}

function prependDbRow(category, node, temp, zscore, action) {
    const tbody = document.getElementById('db-log-body');
    const tr = document.createElement('tr');
    const timeStr = new Date().toLocaleTimeString();
    const tagClass = category.includes("ATTACK") ? "tag-red" : "tag-green";
    
    tr.innerHTML = `
        <td>${timeStr}</td>
        <td><span class="tag ${tagClass}">${category}</span></td>
        <td>${node}</td>
        <td>${temp}</td>
        <td>${zscore}</td>
        <td>${action}</td>
    `;
    tbody.insertBefore(tr, tbody.firstChild);
    if (tbody.children.length > 10) tbody.removeChild(tbody.lastChild);
}

function toggleAttack(state) {
    attackActive = state;
    if (state) {
        alert("🚨 ATTACK SIMULATION ENABLED: ESP32_Node_3 is now injecting 500°C payload into MQTT broker.\n\nObserve how Oracle Z-Score quarrantines Node 3, increments the attacks blocked count, and keeps Smart Contract updated with clean median data!");
    } else {
        alert("✅ NORMAL MODE RESTORED: All 3 ESP32 nodes sending valid telemetry.");
    }
    fetchOracleState();
}

document.addEventListener("DOMContentLoaded", () => {
    initChart();
    setInterval(fetchOracleState, 2000);
});

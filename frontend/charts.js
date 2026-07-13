// =============================================
// charts.js — Chart.js initialization and live updates
// =============================================

let revenueChart;
let sentimentChart;

const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 200 },
    plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(15,18,25,0.95)', borderColor: 'rgba(255,255,255,0.08)', borderWidth: 1, padding: 10, titleColor: '#94a3b8', bodyColor: '#fff', titleFont: { size: 10 }, bodyFont: { size: 12, weight: 'bold' } } },
    scales: {
        x: { grid: { color: 'rgba(30,35,50,0.8)', drawBorder: false }, ticks: { color: '#4b5563', font: { size: 9 }, maxTicksLimit: 8 } },
        y: { grid: { color: 'rgba(30,35,50,0.8)', drawBorder: false }, ticks: { color: '#4b5563', font: { size: 9 } }, beginAtZero: true }
    }
};

export function initCharts() {
    const revCtx = document.getElementById('revenueChart');
    const sentCtx = document.getElementById('sentimentChart');
    if (!revCtx || !sentCtx) return;

    revenueChart = new Chart(revCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99,102,241,0.06)',
                fill: true,
                tension: 0.5,
                pointRadius: 0,
                borderWidth: 2,
            }]
        },
        options: { ...chartDefaults }
    });

    sentimentChart = new Chart(sentCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16,185,129,0.06)',
                fill: true,
                tension: 0.5,
                pointRadius: 0,
                borderWidth: 2,
            }]
        },
        options: { ...chartDefaults, scales: { ...chartDefaults.scales, y: { ...chartDefaults.scales.y, max: 100 } } }
    });
}

export function resetCharts() {
    if (revenueChart) {
        revenueChart.data.labels = [];
        revenueChart.data.datasets[0].data = [];
        revenueChart.update('none');
    }
    if (sentimentChart) {
        sentimentChart.data.labels = [];
        sentimentChart.data.datasets[0].data = [];
        sentimentChart.update('none');
    }
    // Reset live metric displays
    const els = ['total-revenue', 'adoption-rate', 'buyer-count', 'rejector-count', 'revenue-confidence', 'timeline-day-display'];
    const defaults = ['$0', '0%', '0', '0', '—', 'Day 0 / 30'];
    els.forEach((id, i) => { const el = document.getElementById(id); if (el) el.textContent = defaults[i]; });
    const prog = document.getElementById('timeline-progress');
    if (prog) prog.style.width = '0%';
    const evList = document.getElementById('timeline-events-list');
    if (evList) evList.innerHTML = '';
}


export function updateCharts(stats, day, price) {
    const buyers = stats.buyers;
    const rejectors = stats.rejectors;
    const total = stats.total || 1;
    const rev = buyers * price;
    const adoption = ((buyers / total) * 100);
    const variance = rev * 0.05;
    const label = `D${day}`;

    if (revenueChart) {
        revenueChart.data.labels.push(label);
        revenueChart.data.datasets[0].data.push(rev);
        revenueChart.update('none');
    }

    if (sentimentChart) {
        sentimentChart.data.labels.push(label);
        sentimentChart.data.datasets[0].data.push(parseFloat(adoption.toFixed(1)));
        sentimentChart.update('none');
    }

    // Update live metrics in left panel
    const revEl = document.getElementById('total-revenue');
    const revConf = document.getElementById('revenue-confidence');
    const adpEl = document.getElementById('adoption-rate');
    const buyersEl = document.getElementById('buyer-count');
    const rejectEl = document.getElementById('rejector-count');

    if (revEl) revEl.textContent = `$${rev.toLocaleString()}`;
    if (revConf) revConf.textContent = `±$${variance.toLocaleString(undefined, {maximumFractionDigits: 0})} (91% CI)`;
    if (adpEl) adpEl.textContent = `${adoption.toFixed(1)}%`;
    if (buyersEl) buyersEl.textContent = buyers.toLocaleString();
    if (rejectEl) rejectEl.textContent = rejectors.toLocaleString();
}

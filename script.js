// script.js - Frontend Logic for Simulyn MVP

const NUM_NODES = 300;
const STATES = ['state-wait', 'state-buy', 'state-reject'];
const NODE_TYPES = [
    { type: 'consumer', prob: 0.85 },
    { type: 'influencer', prob: 0.10 },
    { type: 'retailer', prob: 0.05 }
];

let nodes = [];
let links = [];
let simulation;
let svg;
let nodeGroup;
let linkGroup;
let isRunning = false;
let currentDay = 1;

// Initialize data
function initData() {
    nodes = Array.from({ length: NUM_NODES }, (_, i) => {
        const rand = Math.random();
        let type = 'consumer';
        let cumulative = 0;
        for (const t of NODE_TYPES) {
            cumulative += t.prob;
            if (rand < cumulative) {
                type = t.type;
                break;
            }
        }
        
        return {
            id: i,
            type: type,
            state: 'state-wait', // Initial state
            age: Math.floor(18 + Math.random() * 50),
            income: Math.floor(30000 + Math.random() * 120000),
            savings: Math.floor(Math.random() * 50000),
            riskTolerance: Math.random(),
            brandLoyalty: Math.random(),
            optimism: Math.random(),
            mood: ['Happy', 'Anxious', 'Neutral', 'Excited', 'Skeptical', 'Optimistic'][Math.floor(Math.random() * 6)],
            goal: ['Buying a bike', 'Saving for house', 'Paying off debt', 'Upgrading phone', 'Investing'][Math.floor(Math.random() * 5)],
            financialStatus: ['Saving money', 'Living paycheck to paycheck', 'Comfortable', 'Struggling', 'Investing heavily'][Math.floor(Math.random() * 5)],
            recentPurchase: ['Laptop', 'Groceries', 'Headphones', 'Shoes', 'Nothing'][Math.floor(Math.random() * 5)],
            recentNegativeExperience: ['Poor delivery', 'Rude support', 'Faulty product', 'Overcharged', 'None'][Math.floor(Math.random() * 5)],
            currentNeed: ['Phone', 'Commute', 'Status symbol', 'Entertainment', 'Utility'][Math.floor(Math.random() * 5)],
            monthlyExpenses: Math.floor(20000 + Math.random() * 50000),
            salaryDay: ['1st', '5th', '15th', 'Last day'][Math.floor(Math.random() * 4)],
            preference: ['Eco-friendly', 'Premium quality', 'Budget', 'Brand name', 'Locally sourced'][Math.floor(Math.random() * 5)]
        };
    });

    // Create random small-world like connections
    for (let i = 0; i < NUM_NODES; i++) {
        const numConnections = nodes[i].type === 'influencer' ? 15 : (nodes[i].type === 'retailer' ? 20 : 3);
        for (let j = 0; j < numConnections; j++) {
            const target = Math.floor(Math.random() * NUM_NODES);
            if (target !== i) {
                links.push({ source: i, target: target });
            }
        }
    }
}

// Initialize D3 Graph
function initGraph() {
    const container = document.getElementById('graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    svg = d3.select('#graph-container').append('svg')
        .attr('width', width)
        .attr('height', height);

    // Zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            svg.selectAll('g').attr('transform', event.transform);
        });
    svg.call(zoom);

    const mainGroup = svg.append('g');

    linkGroup = mainGroup.append('g')
        .selectAll('line')
        .data(links)
        .enter().append('line')
        .attr('class', 'link');

    nodeGroup = mainGroup.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter().append('circle')
        .attr('r', d => d.type === 'influencer' ? 8 : (d.type === 'retailer' ? 10 : 5))
        .attr('class', d => `node-${d.type} ${d.state}`)
        .on('click', handleNodeClick)
        .on('mouseover', showTooltip)
        .on('mouseout', hideTooltip)
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).distance(30))
        .force('charge', d3.forceManyBody().strength(-30))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .on('tick', () => {
            linkGroup
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            nodeGroup
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
        });
}

function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

function showTooltip(event, d) {
    const tooltip = d3.select('#tooltip');
    tooltip.transition().duration(200).style('opacity', .9);
    tooltip.html(`<b>Type:</b> ${d.type}<br/><b>State:</b> ${d.state.replace('state-', '')}`)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
}

function hideTooltip() {
    d3.select('#tooltip').transition().duration(500).style('opacity', 0);
}

// UI Interactions
function handleNodeClick(event, d) {
    document.getElementById('agent-empty').classList.add('hidden');
    document.getElementById('reason-empty').classList.add('hidden');
    document.getElementById('agent-details').classList.remove('hidden');
    document.getElementById('reason-details').classList.remove('hidden');

    document.getElementById('agent-id').innerText = `Agent #${d.id}`;
    document.getElementById('agent-type').innerText = d.type;
    document.getElementById('agent-avatar').innerText = d.id;
    document.getElementById('agent-age').innerText = d.age;
    document.getElementById('agent-income').innerText = `$${d.income.toLocaleString()}`;
    document.getElementById('agent-savings').innerText = `$${d.savings.toLocaleString()}`;
    document.getElementById('agent-expenses').innerText = `$${d.monthlyExpenses.toLocaleString()}`;
    document.getElementById('agent-payday').innerText = d.salaryDay;
    document.getElementById('agent-mood').innerText = d.mood;
    document.getElementById('agent-status').innerText = d.financialStatus;
    document.getElementById('agent-goal').innerText = d.goal;
    document.getElementById('agent-need').innerText = d.currentNeed;
    document.getElementById('agent-buy').innerText = d.recentPurchase;
    document.getElementById('agent-bad').innerText = d.recentNegativeExperience;
    document.getElementById('agent-pref').innerText = d.preference;
    
    let actionTxt = d.state.replace('state-', '').toUpperCase();
    if(actionTxt === 'BUY') actionTxt = 'PREORDERED';
    if(actionTxt === 'REJECT') actionTxt = 'COMPLAINED';
    document.getElementById('agent-action').innerText = actionTxt;

    // Randomize bars for demo
    const priceScore = Math.floor(Math.random() * 100);
    const peerScore = Math.floor(Math.random() * 100);
    const trustScore = Math.floor(Math.random() * 100);
    
    document.getElementById('bar-price').style.width = `${priceScore}%`;
    document.getElementById('score-price').innerText = `${priceScore}%`;
    document.getElementById('bar-peer').style.width = `${peerScore}%`;
    document.getElementById('score-peer').innerText = `${peerScore}%`;
    document.getElementById('bar-trust').style.width = `${trustScore}%`;
    document.getElementById('score-trust').innerText = `${trustScore}%`;

    // Fetch AI Reasoning from backend
    const price = document.getElementById('price-slider').value;
    const product = document.getElementById('product-name').value;
    
    document.getElementById('ai-why').innerHTML = `<span class="text-gray-500 animate-pulse">Generating reasoning...</span>`;
    document.getElementById('ai-change').innerText = '...';
    document.getElementById('ai-conf').innerText = '--';
    document.getElementById('ai-factor').innerText = '--';
    
    fetch('http://127.0.0.1:8000/generate_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            agent_id: d.id,
            agent_type: d.type,
            mood: d.mood,
            income: d.income,
            product: product,
            price: parseInt(price),
            state: d.state.replace('state-', ''),
            goal: d.goal,
            savings: d.savings,
            financial_status: d.financialStatus,
            recent_purchase: d.recentPurchase,
            recent_negative_experience: d.recentNegativeExperience,
            current_need: d.currentNeed,
            monthly_expenses: d.monthlyExpenses,
            salary_day: d.salaryDay,
            preference: d.preference
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('ai-why').innerText = `"${data.why}"`;
        document.getElementById('ai-change').innerText = `"${data.what_would_change}"`;
        document.getElementById('ai-conf').innerText = data.confidence;
        document.getElementById('ai-factor').innerText = data.most_influential_factor;
    })
    .catch(err => {
        console.warn("API failed, using panic mode cache:", err);
        document.getElementById('ai-why').innerText = `"Error reaching intelligence engine."`;
        document.getElementById('ai-change').innerText = `"..."`;
    });
}

// Sliders and setup
document.getElementById('price-slider').addEventListener('input', e => document.getElementById('price-val').innerText = `$${e.target.value}`);
document.getElementById('marketing-slider').addEventListener('input', e => document.getElementById('marketing-val').innerText = `$${e.target.value}M`);
document.getElementById('sentiment-slider').addEventListener('input', e => document.getElementById('sentiment-val').innerText = e.target.value);

// Simulation Engine Mock
document.getElementById('run-sim-btn').addEventListener('click', async () => {
    if (isRunning) return;
    isRunning = true;
    currentDay = 1;
    document.getElementById('time-slider').value = 1;
    document.getElementById('run-sim-btn').innerText = 'Simulating...';
    document.getElementById('run-sim-btn').classList.replace('bg-accent', 'bg-gray-600');
    
    const price = parseInt(document.getElementById('price-slider').value);
    
    // Actual API call to AMD backend
    document.getElementById('cpu-time').innerText = 'Computing...';
    document.getElementById('gpu-time').innerText = 'Computing...';

    fetch('http://127.0.0.1:8000/benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_nodes: 2500 }) // Heavy workload to demonstrate difference
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            document.getElementById('cpu-time').innerText = 'Backend Error';
            document.getElementById('gpu-time').innerText = 'Backend Error';
            return;
        }
        document.getElementById('cpu-time').innerText = `${data.cpu_time_sec}s`;
        document.getElementById('gpu-time').innerText = data.hardware_accelerated ? `${data.gpu_time_sec}s` : `N/A (CPU fallback)`;
    })
    .catch(err => {
        console.error("Backend offline:", err);
        document.getElementById('cpu-time').innerText = 'Backend offline';
        document.getElementById('gpu-time').innerText = 'Backend offline';
    });

    // Timeline loop
    const interval = setInterval(() => {
        if (currentDay > 30) {
            clearInterval(interval);
            isRunning = false;
            document.getElementById('run-sim-btn').innerText = 'Run Simulation';
            document.getElementById('run-sim-btn').classList.replace('bg-gray-600', 'bg-accent');
            
            // Update Scenario A stats
            const buys = nodes.filter(n => n.state === 'state-buy').length;
            const rejects = nodes.filter(n => n.state === 'state-reject').length;
            const waits = nodes.filter(n => n.state === 'state-wait').length;
            const adoption = Math.round((buys / NUM_NODES) * 100);
            const rev = buys * price * 1000; // Mock scaling
            
            document.getElementById('scenario-a-adopt').innerText = `${adoption}%`;
            document.getElementById('scenario-a-rev').innerText = `$${(rev/1000000).toFixed(1)}M`;
            
            // Trigger Executive Summary
            const mBudget = parseInt(document.getElementById('marketing-slider').value) * 1000000;
            const product = document.getElementById('product-name').value;
            fetch('http://127.0.0.1:8000/executive_summary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    product: product,
                    price: price,
                    marketing_budget: mBudget,
                    total_buyers: buys,
                    total_rejectors: rejects,
                    total_waiting: waits
                })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('exec-adoption').innerText = data.market_adoption;
                document.getElementById('exec-revenue').innerText = data.expected_revenue;
                document.getElementById('exec-risk').innerText = data.risk_score;
                document.getElementById('exec-summary-text').innerText = data.mckinsey_summary;
                
                const strategiesHTML = data.strategies.map(s => `
                    <div class="bg-gray-800 border ${data.recommended_strategy === s.name ? 'border-accent shadow-md' : 'border-gray-700'} rounded p-3 relative">
                        ${data.recommended_strategy === s.name ? '<span class="absolute top-0 right-0 bg-accent text-white text-[9px] font-bold px-2 py-0.5 rounded-bl rounded-tr uppercase">Recommended</span>' : ''}
                        <h4 class="text-white text-sm font-bold mb-1">${s.name}</h4>
                        <div class="flex justify-between text-xs mb-2">
                            <span class="text-gray-400">Probability: <span class="text-white">${s.probability}</span></span>
                            <span class="text-gray-400">Expected: <span class="text-success font-bold">${s.expected_revenue}</span></span>
                        </div>
                        <p class="text-xs text-gray-500">${s.reason}</p>
                    </div>
                `).join('');
                document.getElementById('exec-strategies').innerHTML = strategiesHTML;
                document.getElementById('exec-modal').classList.remove('hidden');
            });
            
            return;
        }

        document.getElementById('time-slider').value = currentDay;
        document.getElementById('current-day-label').innerText = `Day ${currentDay}`;

        // Deterministic diffusion logic based on memory
        nodes.forEach(n => {
            if (n.state === 'state-wait') {
                let buyScore = 0;
                let rejectScore = 0;

                // Affordability
                if (n.savings > price) buyScore += 2;
                else if (n.monthlyExpenses > n.income / 12) rejectScore += 3;

                // Mood and Financial Status
                if (n.mood === 'Optimistic' || n.mood === 'Excited' || n.mood === 'Happy') buyScore += 1;
                if (n.financialStatus === 'Saving money' || n.financialStatus === 'Struggling') rejectScore += 2;
                if (n.financialStatus === 'Comfortable' || n.financialStatus === 'Investing heavily') buyScore += 1;

                // Needs and Preferences
                if (n.currentNeed === 'Phone' || n.currentNeed === 'Status symbol') buyScore += 2;
                if (n.recentNegativeExperience !== 'None') rejectScore += 1;
                
                // Timing (Payday simulation)
                const isPayday = (n.salaryDay === '1st' && currentDay <= 3) || 
                                 (n.salaryDay === '5th' && currentDay >= 4 && currentDay <= 6) ||
                                 (n.salaryDay === '15th' && currentDay >= 14 && currentDay <= 16) ||
                                 (n.salaryDay === 'Last day' && currentDay >= 28);
                if (isPayday) buyScore += 2;

                // Price threshold based on preference
                const perceivedValue = n.preference === 'Premium quality' ? price * 0.8 : price;
                if (perceivedValue > 800) rejectScore += 2;
                if (perceivedValue < 300) buyScore += 1;

                // Add some randomness
                buyScore += Math.random() * 2;
                rejectScore += Math.random() * 2;

                if (buyScore > 5 && buyScore > rejectScore) {
                    n.state = 'state-buy';
                } else if (rejectScore > 4 && rejectScore > buyScore) {
                    n.state = 'state-reject';
                }
            }
        });

        // Update D3 nodes
        nodeGroup.attr('class', d => `node-${d.type} ${d.state}`);

        currentDay++;
    }, 300);
});

// Init
window.onload = () => {
    initData();
    initGraph();
};

// PDF Export
document.getElementById('export-pdf-btn').addEventListener('click', () => {
    const btn = document.getElementById('export-pdf-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span class="animate-pulse">Generating PDF...</span>`;
    
    const element = document.body;
    const opt = {
        margin:       0,
        filename:     'Simulyn_Report.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' }
    };
    
    html2pdf().set(opt).from(element).outputPdf('blob').then(function(pdfBlob) {
        const blobUrl = window.URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = 'Simulyn_Report.pdf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(blobUrl);
        btn.innerHTML = originalText;
    });
});

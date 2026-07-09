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
            mood: ['Happy', 'Anxious', 'Neutral', 'Excited', 'Skeptical'][Math.floor(Math.random() * 5)]
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
    document.getElementById('agent-risk').innerText = d.riskTolerance.toFixed(2);
    document.getElementById('agent-brand').innerText = d.brandLoyalty.toFixed(2);
    document.getElementById('agent-mood').innerText = d.mood;
    
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
    
    document.getElementById('ai-chat-content').innerHTML = `<span class="text-gray-500 animate-pulse">Generating reasoning...</span>`;
    
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
            state: d.state.replace('state-', '')
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('ai-chat-content').innerText = `"${data.chat}"`;
    })
    .catch(err => {
        console.warn("API failed, using panic mode cache:", err);
        // Panic Mode Fallback
        let reason = "";
        if (d.state === 'state-buy') {
            reason = `"I've been looking for something exactly like the ${product}. Even at $${price}, my brand loyalty is high and my friends are hyping it up."`;
        } else if (d.state === 'state-reject') {
            reason = `"Are they crazy? $${price} is way too much given my current savings. Plus, I saw a terrible review from an influencer I follow."`;
        } else {
            reason = `"I'm keeping an eye on this. The price is $${price}, which is steep. I'll wait to see if it goes on sale or if my network buys it first."`;
        }
        document.getElementById('ai-chat-content').innerHTML = `<i><span class="text-xs text-orange-500 mb-1 block">[Using cached explanation]</span>${reason}</i>`;
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
            const adoption = Math.round((buys / NUM_NODES) * 100);
            const rev = buys * price * 1000; // Mock scaling
            
            document.getElementById('scenario-a-adopt').innerText = `${adoption}%`;
            document.getElementById('scenario-a-rev').innerText = `$${(rev/1000000).toFixed(1)}M`;
            return;
        }

        document.getElementById('time-slider').value = currentDay;
        document.getElementById('current-day-label').innerText = `Day ${currentDay}`;

        // Simple diffusion mock logic
        nodes.forEach(n => {
            if (n.state === 'state-wait') {
                const chance = Math.random();
                // Higher price = lower chance of buy
                const threshold = price > 400 ? 0.95 : 0.85;
                if (chance > threshold) n.state = 'state-buy';
                else if (chance < 0.1) n.state = 'state-reject';
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

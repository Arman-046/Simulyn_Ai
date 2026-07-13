// =============================================
// graph.js — D3.js Synthetic Economy graph
// Agents are regenerated per scenario for accurate simulation
// =============================================

export const NUM_NODES = 300;
export let nodes = [];
export let links = [];
export let simulation;
let svgEl, nodeGroup, linkGroup, zoomGroup;

export function getNodeGroup() { return nodeGroup; }

export function initData(popData) {
    if (popData && popData.agents && popData.links) {
        if (popData.agents.length > 500) {
            nodes = popData.agents.slice(0, 500);
            const validIds = new Set(nodes.map(n => n.id));
            links = popData.links.filter(l => validIds.has(l.source) && validIds.has(l.target));
            
            let indicator = document.getElementById('downsample-indicator');
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.id = 'downsample-indicator';
                indicator.style = "position:absolute; bottom:12px; right:12px; color:#94a3b8; font-size:11px; z-index:50; background: rgba(15,18,25,0.8); padding: 4px 8px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);";
                const container = document.getElementById('graph-container');
                if (container) container.appendChild(indicator);
            }
            indicator.textContent = `Visualizing 500 of ${popData.agents.length.toLocaleString()} agents`;
            indicator.style.display = 'block';
        } else {
            nodes = popData.agents;
            links = popData.links;
            const indicator = document.getElementById('downsample-indicator');
            if (indicator) indicator.style.display = 'none';
        }
    }
}

export function initGraph(onNodeClick, popData) {
    initData(popData);
    const container = document.getElementById('graph-container');
    if (!container) return;

    // Clear any previous graph
    d3.select('#graph-container').selectAll('svg').remove();

    const W = container.clientWidth;
    const H = container.clientHeight;

    svgEl = d3.select('#graph-container').append('svg')
        .attr('width', W).attr('height', H)
        .style('position', 'absolute').style('inset', '0');

    // Zoom removed per user request
    zoomGroup = svgEl.append('g');

    linkGroup = zoomGroup.append('g')
        .selectAll('line').data(links).enter().append('line')
        .attr('class', 'link');

    nodeGroup = zoomGroup.append('g')
        .selectAll('circle').data(nodes).enter().append('circle')
        .attr('r', d => d.type === 'influencer' ? 7 : d.type === 'retailer' ? 9 : 3.5)
        .attr('class', d => `node-${d.type} ${d.state}`)
        .style('cursor', 'pointer')
        .on('click', (_, d) => onNodeClick(d))
        .on('mouseover', (event, d) => {
            const tip = document.getElementById('d3-tooltip');
            if (!tip) return;
            const stateLabel = d.state === 'state-buy' ? '✓ Bought' : d.state === 'state-reject' ? '✗ Rejected' : '⏳ Waiting';
            tip.innerHTML = `<div style="color:#94a3b8;font-size:10px;text-transform:uppercase;letter-spacing:.05em;">${d.type}</div><div style="font-weight:600;color:#fff;font-size:12px;">${d.profession}</div><div style="color:#4b5563;font-size:11px;">${d.location} · $${d.income.toLocaleString()}/yr</div><div style="font-size:11px;margin-top:4px;">${stateLabel}</div>`;
            tip.style.opacity = '1';
            tip.style.left = (event.clientX + 14) + 'px';
            tip.style.top = (event.clientY - 8) + 'px';
        })
        .on('mousemove', event => {
            const tip = document.getElementById('d3-tooltip');
            if (tip) { tip.style.left = (event.clientX + 14) + 'px'; tip.style.top = (event.clientY - 8) + 'px'; }
        })
        .on('mouseout', () => { const tip = document.getElementById('d3-tooltip'); if (tip) tip.style.opacity = '0'; })
        .call(d3.drag()
            .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
            .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
            .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));

    simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).distance(40).strength(0.15))
        .force('charge', d3.forceManyBody().strength(-35))
        .force('center', d3.forceCenter(W / 2, H / 2))
        .force('collision', d3.forceCollide(9))
        .alphaDecay(0.04) // Cools down faster to reduce animation heaviness
        .on('tick', () => {
            linkGroup.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
            nodeGroup.attr('cx', d => d.x).attr('cy', d => d.y);
        });
}

export function refreshNodeStyles() {
    if (nodeGroup) nodeGroup.attr('class', d => `node-${d.type} ${d.state}`);
}

export function rebuildGraph(scenario, onNodeClick, popData) {
    initData(popData);

    if (!zoomGroup) return; // graph not rendered yet
    d3.select('#graph-container').selectAll('svg').remove();
    initGraph(onNodeClick, popData);
}

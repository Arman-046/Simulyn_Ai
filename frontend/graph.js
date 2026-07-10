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

const PROFESSIONS_BY_REGION = {
    "North America": ['Software Engineer', 'Teacher', 'Designer', 'Student', 'Manager', 'Doctor', 'Analyst', 'Entrepreneur', 'Nurse', 'Sales Rep'],
    "United Kingdom": ['Software Engineer', 'Teacher', 'Consultant', 'Student', 'Manager', 'Doctor', 'Analyst', 'Barista', 'Accountant', 'Solicitor'],
    "India": ['Software Engineer', 'Teacher', 'Designer', 'Student', 'Business Owner', 'Doctor', 'Analyst', 'Shopkeeper', 'Engineer', 'Freelancer'],
    "Europe": ['Software Engineer', 'Teacher', 'Designer', 'Student', 'Manager', 'Doctor', 'Analyst', 'Entrepreneur', 'Civil Servant', 'Researcher'],
    "Asia Pacific": ['Software Engineer', 'Factory Worker', 'Designer', 'Student', 'Manager', 'Doctor', 'Analyst', 'Entrepreneur', 'Trader', 'Teacher'],
    "default": ['Engineer', 'Teacher', 'Designer', 'Student', 'Manager', 'Doctor', 'Analyst', 'Entrepreneur'],
};

const CITIES_BY_REGION = {
    "North America": ['New York', 'San Francisco', 'Chicago', 'Austin', 'Seattle', 'Boston', 'Los Angeles', 'Denver'],
    "United Kingdom": ['London', 'Manchester', 'Birmingham', 'Edinburgh', 'Bristol', 'Leeds', 'Liverpool', 'Oxford'],
    "India": ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Ahmedabad'],
    "Europe": ['Berlin', 'Paris', 'Amsterdam', 'Stockholm', 'Barcelona', 'Vienna', 'Prague', 'Zurich'],
    "Asia Pacific": ['Tokyo', 'Singapore', 'Shanghai', 'Seoul', 'Sydney', 'Melbourne', 'Bangkok', 'Jakarta'],
    "default": ['City A', 'City B', 'City C', 'Suburban', 'Rural'],
};

// Income ranges (annual, in USD equivalent) by region
const INCOME_RANGES = {
    "North America": { min: 30000, max: 200000 },
    "United Kingdom": { min: 25000, max: 160000 },
    "India": { min: 5000, max: 60000 },   // USD equivalent
    "Europe": { min: 22000, max: 130000 },
    "Asia Pacific": { min: 15000, max: 120000 },
    "default": { min: 20000, max: 150000 },
};

const MOODS = ['Optimistic', 'Anxious', 'Neutral', 'Excited', 'Skeptical'];
const GOALS = ['Saving for house', 'Paying off debt', 'Upgrading tech', 'Investing', 'Building emergency fund'];
const FIN_STATUS = ['Saving money', 'Living paycheck to paycheck', 'Comfortable', 'Struggling', 'Investing heavily'];
const PURCHASES = ['Laptop', 'Headphones', 'Shoes', 'Nothing', 'Subscription', 'Phone'];
const NEG_EXP = ['Poor delivery', 'Faulty product', 'Overcharged', 'None', 'None', 'None'];
const NEEDS = ['Phone', 'Commute', 'Status symbol', 'Entertainment', 'Utility', 'Productivity'];
const SALARY_DAYS = ['1st', '5th', '15th', 'Last day'];
const PREFS = ['Eco-friendly', 'Premium quality', 'Budget', 'Brand name', 'Locally sourced', 'Tech-forward'];

function seededRandom(seed) {
    let s = seed >>> 0;
    s ^= s << 13; s ^= s >> 17; s ^= s << 5;
    return (s >>> 0) / 4294967296;
}

function buildSeedFromScenario(scenario) {
    const str = (scenario?.product_name?.value || '') +
        (scenario?.launch_region?.value || '') +
        (scenario?.price?.value || '') +
        (scenario?.target_audience?.value || '');
    let hash = 5381;
    for (let i = 0; i < str.length; i++) hash = ((hash << 5) + hash) + str.charCodeAt(i);
    return hash >>> 0;
}

function getAudienceBias(audience = '', scenario = {}) {
    const a = audience.toLowerCase();
    const price = Number(scenario?.price?.value) || 100;
    const segment = (scenario?.market_segment?.value || '').toLowerCase();

    let moodBias = {}; // empty = uniform
    let financeBias = 0; // positive = wealthier agents
    let ageBias = { min: 18, max: 68 };
    let prefBias = '';

    if (a.includes('professional') || a.includes('enterprise') || a.includes('b2b')) {
        financeBias = 0.4; ageBias = { min: 28, max: 55 }; prefBias = 'Premium quality';
    }
    if (a.includes('student') || a.includes('youth') || a.includes('gen z')) {
        financeBias = -0.5; ageBias = { min: 18, max: 28 }; prefBias = 'Budget';
    }
    if (a.includes('senior') || a.includes('elderly') || a.includes('retiree')) {
        ageBias = { min: 55, max: 80 }; prefBias = 'Brand name';
    }
    if (a.includes('executive') || a.includes('c-suite') || a.includes('hni') || a.includes('high')) {
        financeBias = 0.7; ageBias = { min: 35, max: 65 }; prefBias = 'Premium quality';
    }
    if (segment.includes('premium') || segment.includes('luxury')) {
        financeBias = Math.max(financeBias, 0.3);
        prefBias = prefBias || 'Premium quality';
    }
    if (segment.includes('budget') || segment.includes('value') || segment.includes('mass')) {
        financeBias = Math.min(financeBias, -0.2);
        prefBias = prefBias || 'Budget';
    }

    return { financeBias, ageBias, prefBias };
}

/**
 * (Re-)generate agent population based on the current scenario.
 * Call this every time a new scenario is loaded.
 */
export function initData(scenario = null) {
    const region = scenario?.launch_region?.value || 'North America';
    const audience = scenario?.target_audience?.value || '';
    const price = Number(scenario?.price?.value) || 100;

    const professions = PROFESSIONS_BY_REGION[region] || PROFESSIONS_BY_REGION["default"];
    const cities = CITIES_BY_REGION[region] || CITIES_BY_REGION["default"];
    const incomeRange = INCOME_RANGES[region] || INCOME_RANGES["default"];

    const bias = getAudienceBias(audience, scenario);
    const seed = buildSeedFromScenario(scenario);

    nodes = Array.from({ length: NUM_NODES }, (_, i) => {
        const r = seededRandom(seed ^ (i * 7919));
        const type = r < 0.05 ? 'retailer' : r < 0.15 ? 'influencer' : 'consumer';

        // Seeded random for each attribute
        const rng = (offset) => seededRandom(seed ^ (i * 7919 + offset * 1000003));

        // Income — biased toward target audience
        const incomeBase = incomeRange.min + rng(1) * (incomeRange.max - incomeRange.min);
        const incomeBiased = Math.max(incomeRange.min, incomeBase * (1 + bias.financeBias * 0.8));
        const income = Math.floor(incomeBiased);

        // Savings — correlated with income
        const savingsRatio = 0.05 + rng(2) * 0.6; // 5%–65% of income
        const savings = Math.floor(income * savingsRatio);

        // Monthly expenses — realistic
        const monthlyExpenses = Math.floor((income / 12) * (0.4 + rng(3) * 0.5));

        // Age — biased toward target
        const age = Math.floor(bias.ageBias.min + rng(4) * (bias.ageBias.max - bias.ageBias.min));

        // Preference — biased toward segment
        let preference;
        if (bias.prefBias && rng(5) > 0.35) {
            preference = bias.prefBias;
        } else {
            preference = PREFS[Math.floor(rng(5) * PREFS.length)];
        }

        return {
            id: i,
            type,
            state: 'state-wait',
            age,
            income,
            savings,
            riskTolerance: rng(6),
            brandLoyalty: rng(7),
            mood: MOODS[Math.floor(rng(8) * MOODS.length)],
            goal: GOALS[Math.floor(rng(9) * GOALS.length)],
            financialStatus: FIN_STATUS[Math.floor(rng(10) * FIN_STATUS.length)],
            recentPurchase: PURCHASES[Math.floor(rng(11) * PURCHASES.length)],
            recentNegativeExperience: NEG_EXP[Math.floor(rng(12) * NEG_EXP.length)],
            currentNeed: NEEDS[Math.floor(rng(13) * NEEDS.length)],
            monthlyExpenses,
            salaryDay: SALARY_DAYS[Math.floor(rng(14) * SALARY_DAYS.length)],
            preference,
            location: cities[Math.floor(rng(15) * cities.length)],
            profession: professions[Math.floor(rng(16) * professions.length)],
            influenceScore: Math.floor(rng(17) * 100),
            buyingPower: Math.floor(rng(18) * 100),
        };
    });

    // Rebuild links
    links = [];
    for (let i = 0; i < NUM_NODES; i++) {
        const conns = nodes[i].type === 'influencer' ? 20 : nodes[i].type === 'retailer' ? 25 : 3;
        for (let j = 0; j < conns; j++) {
            const t = Math.floor(seededRandom(seed ^ (i * 31337 + j * 999983)) * NUM_NODES);
            if (t !== i) links.push({ source: i, target: t });
        }
    }
}

export function initGraph(onNodeClick) {
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

export function rebuildGraph(scenario, onNodeClick) {
    initData(scenario);

    if (!zoomGroup) return; // graph not rendered yet
    d3.select('#graph-container').selectAll('svg').remove();
    initGraph(onNodeClick);
}

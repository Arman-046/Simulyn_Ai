// =============================================
// simulation.js — Scenario-aware stochastic simulation engine
// =============================================

import { nodes, initData, refreshNodeStyles } from './graph.js';
import { updateCharts } from './charts.js';
import { checkNarrativeEvents } from './events.js';

let isRunning = false;
let currentDay = 1;
let intervalId = null;
let scenarioSeed = 0;
let playbackSpeed = 250;
let simScenario = null;
let onCompleteCallback = null;
let _onNodeClick = null; // kept for graph rebuild reference

// Deterministic seeded RNG (xorshift-based, reproducible)
function seededRandom(seed) {
    let s = seed >>> 0;
    s ^= s << 13; s ^= s >> 17; s ^= s << 5;
    return (s >>> 0) / 4294967296;
}

function buildSeed(scenario) {
    const str = (scenario?.product_name?.value || '') +
        (scenario?.launch_region?.value || '') +
        (scenario?.price?.value || '') +
        (scenario?.target_audience?.value || '');
    let hash = 5381;
    for (let i = 0; i < str.length; i++) hash = ((hash << 5) + hash) + str.charCodeAt(i);
    return hash >>> 0;
}

export function initSimulation(scenario, onNodeClick) {
    simScenario = scenario;
    scenarioSeed = buildSeed(scenario);
    currentDay = 1;
    isRunning = false;
    clearInterval(intervalId);
    _onNodeClick = onNodeClick;

    // Re-generate scenario-specific agents
    initData(scenario);

    // Reset all nodes to wait state
    nodes.forEach(n => { n.state = 'state-wait'; });
    refreshNodeStyles();
}

export function startSimulation(onComplete) {
    if (isRunning || !simScenario) return;
    onCompleteCallback = onComplete;
    isRunning = true;

    intervalId = setInterval(() => {
        if (currentDay > 30) {
            stopSimulation();
            if (typeof onCompleteCallback === 'function') onCompleteCallback();
            return;
        }
        stepDay();
    }, playbackSpeed);
}

export function pauseSimulation() {
    isRunning = false;
    clearInterval(intervalId);
}

export function stopSimulation() {
    isRunning = false;
    clearInterval(intervalId);
}

export function setPlaybackSpeed(speed) {
    const wasRunning = isRunning;
    playbackSpeed = speed;
    if (wasRunning) {
        pauseSimulation();
        startSimulation(onCompleteCallback);
    }
}

export function getSimulationState() {
    return {
        day: currentDay,
        buyers: nodes.filter(n => n.state === 'state-buy').length,
        rejectors: nodes.filter(n => n.state === 'state-reject').length,
        waiting: nodes.filter(n => n.state === 'state-wait').length,
    };
}

function getScenarioModifiers(scenario) {
    const price = Number(scenario?.price?.value) || 100;
    const budget = Number(scenario?.marketing_budget?.value) || 500000;
    const segment = (scenario?.market_segment?.value || '').toLowerCase();
    const region = scenario?.launch_region?.value || 'North America';
    const category = (scenario?.category?.value || '').toLowerCase();
    const usp = (scenario?.usp?.value || '').toLowerCase();
    const audience = (scenario?.target_audience?.value || '').toLowerCase();

    let marketingBoost = 0;
    if (budget > 5_000_000) marketingBoost = 0.8;
    else if (budget > 1_000_000) marketingBoost = 0.5;
    else if (budget > 100_000) marketingBoost = 0.2;
    else marketingBoost = -0.3; // low budget = harder adoption

    let premiumBias = 0;
    if (segment.includes('premium') || segment.includes('luxury')) premiumBias = 1.0;
    else if (segment.includes('budget') || segment.includes('value') || segment.includes('mass')) premiumBias = -0.5;

    // Category-specific modifiers
    let categoryBoost = 0;
    if (category.includes('saas') || category.includes('software')) categoryBoost = 0.3; // recurring = easier
    if (category.includes('wearable') || category.includes('ar') || category.includes('vr')) categoryBoost = 0.2; // novelty
    if (category.includes('fmcg') || category.includes('consumer goods')) categoryBoost = 0.4; // impulse buy

    // USP alignment
    let uspBoost = 0;
    if (usp.includes('premium') || usp.includes('quality')) uspBoost = 0.2;
    if (usp.includes('affordable') || usp.includes('cheap') || usp.includes('budget')) uspBoost = 0.3;
    if (usp.includes('ai') || usp.includes('innovative') || usp.includes('unique')) uspBoost = 0.25;

    // Region economic context
    let regionBias = 0;
    if (region === 'North America' || region === 'United Kingdom' || region === 'Europe') regionBias = 0;
    if (region === 'India' && price > 500) regionBias = -0.5; // high price in price-sensitive market
    if (region === 'India' && price < 50) regionBias = 0.6; // very affordable in India

    return {
        marketingBoost,
        premiumBias,
        categoryBoost,
        uspBoost,
        regionBias,
        price,
    };
}

function stepDay() {
    const mods = getScenarioModifiers(simScenario);
    const price = mods.price;
    const eventModifiers = checkNarrativeEvents(currentDay, simScenario, scenarioSeed);

    nodes.forEach(n => {
        if (n.state !== 'state-wait') return;

        let buyScore = 0;
        let rejectScore = 0;

        // ── Financial capacity (relative to price) ──────────────────────────
        const annualAffordability = n.income * 0.04; // willing to spend ~4% of income/yr
        const priceToAffordRatio = price / annualAffordability;

        if (priceToAffordRatio < 0.3) buyScore += 3;       // very affordable
        else if (priceToAffordRatio < 0.7) buyScore += 1.5; // affordable
        else if (priceToAffordRatio < 1.2) buyScore += 0;   // borderline
        else if (priceToAffordRatio < 2.0) rejectScore += 1.5; // stretch
        else rejectScore += 3;                              // unaffordable

        if (n.savings > price * 2) buyScore += 2;
        else if (n.savings > price) buyScore += 1;
        else if (n.savings < price * 0.5) rejectScore += 1.5;

        if (n.income > 100000) buyScore += 1;
        else if (n.income < 25000) rejectScore += 1.5;

        const budgetPressure = (n.monthlyExpenses / (n.income / 12));
        if (budgetPressure > 0.85) rejectScore += 2; // living paycheck to paycheck
        else if (budgetPressure < 0.5) buyScore += 0.5;

        // ── Psychological / behavioral ───────────────────────────────────────
        if (n.mood === 'Optimistic' || n.mood === 'Excited') buyScore += 1.2;
        else if (n.mood === 'Anxious' || n.mood === 'Skeptical') rejectScore += 1;

        if (n.financialStatus === 'Comfortable' || n.financialStatus === 'Investing heavily') buyScore += 1;
        if (n.financialStatus === 'Struggling' || n.financialStatus === 'Living paycheck to paycheck') rejectScore += 2;

        // ── Needs & preferences ─────────────────────────────────────────────
        if (n.currentNeed === 'Status symbol' && mods.premiumBias >= 0) buyScore += 1.5;
        if (n.currentNeed === 'Productivity' || n.currentNeed === 'Utility') buyScore += 0.8;
        if (n.preference === 'Premium quality' && mods.premiumBias > 0) buyScore += 1.5;
        if (n.preference === 'Budget' && price > 200) rejectScore += 1.5;
        if (n.preference === 'Tech-forward') buyScore += 0.8;

        // ── Negative experience ─────────────────────────────────────────────
        if (n.recentNegativeExperience !== 'None') rejectScore += 0.8;

        // ── Paycheck timing ─────────────────────────────────────────────────
        const isPayday = (n.salaryDay === '1st' && currentDay <= 2) ||
            (n.salaryDay === '5th' && currentDay >= 4 && currentDay <= 6) ||
            (n.salaryDay === '15th' && currentDay >= 14 && currentDay <= 16) ||
            (n.salaryDay === 'Last day' && currentDay >= 28);
        if (isPayday) buyScore += 2;

        // ── Risk tolerance ──────────────────────────────────────────────────
        buyScore += n.riskTolerance * 0.8;

        // ── Influence score (influencer/retailer boost) ─────────────────────
        if (n.type === 'influencer') buyScore += 1.5;
        if (n.type === 'retailer') buyScore += 1;
        buyScore += n.influenceScore / 200;

        // ── Scenario-level modifiers ─────────────────────────────────────────
        buyScore += mods.marketingBoost;
        buyScore += mods.categoryBoost;
        buyScore += mods.uspBoost;
        buyScore += mods.regionBias;

        // ── Event modifiers ─────────────────────────────────────────────────
        buyScore += eventModifiers.buyBoost;
        rejectScore += eventModifiers.rejectBoost;

        // ── Controlled seeded noise ─────────────────────────────────────────
        const buyNoise = seededRandom(scenarioSeed ^ (n.id * 7919 + currentDay * 31)) * 1.5;
        const rejNoise = seededRandom(scenarioSeed ^ (n.id * 6271 + currentDay * 53 + 9999)) * 1.5;
        buyScore += buyNoise;
        rejectScore += rejNoise;

        // ── Decision threshold ──────────────────────────────────────────────
        if (buyScore > 6.0 && buyScore > rejectScore) n.state = 'state-buy';
        else if (rejectScore > 5.0 && rejectScore > buyScore) n.state = 'state-reject';
    });

    refreshNodeStyles();
    updateCharts(nodes, currentDay, price);

    // Update progress bar and day counter
    const progress = document.getElementById('timeline-progress');
    const dayDisplay = document.getElementById('timeline-day-display');
    if (progress) progress.style.width = `${(currentDay / 30) * 100}%`;
    if (dayDisplay) dayDisplay.textContent = `Day ${currentDay} / 30`;

    document.dispatchEvent(new CustomEvent('simulation-step', { detail: { day: currentDay } }));
    currentDay++;
}

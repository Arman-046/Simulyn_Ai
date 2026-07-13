// =============================================
// simulation.js — PyTorch-powered simulation engine client
// =============================================

import { nodes, links, initData, refreshNodeStyles } from './graph.js';
import { updateCharts } from './charts.js';
import { checkNarrativeEvents } from './events.js';
import { runSimulation } from './api.js';

let isRunning = false;
let currentDay = 1;
let intervalId = null;
let playbackSpeed = 250;
let simScenario = null;
let onCompleteCallback = null;
let simulationHistory = [];
export let globalSimulationStats = { buyers: 0, rejectors: 0, waiting: 0, total: 0 };
let totalPopSize = 0;

export async function initSimulation(scenario, popData) {
    totalPopSize = popData?.agents?.length || 0;
    simScenario = scenario;
    currentDay = 1;
    isRunning = false;
    clearInterval(intervalId);

    // Reset all nodes to wait state
    nodes.forEach(n => { n.state = 'state-wait'; });
    refreshNodeStyles();
    
    try {
        console.log("[Simulyn] Calling PyTorch Neural Economic Engine...");
        
        const simId = popData?.simulation_id;
        if (!simId) throw new Error("No simulation_id returned from backend.");
        
        const res = await runSimulation(simId);
        simulationHistory = res.history || [];
        window.reasoningTraces = res.reasoning_traces || [];
        console.log(`[Simulyn] Received simulation tensor using device: ${res.device}`);
    } catch (e) {
        console.error("[Simulyn] PyTorch engine error (fallback to blank):", e);
        // Fallback: 30 days of just waiting
        simulationHistory = Array.from({length: 30}, () => Array(300).fill(0));
        window.reasoningTraces = [];
    }
}

export function startSimulation(onComplete) {
    if (isRunning || !simScenario || simulationHistory.length === 0) return;
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
        buyers: globalSimulationStats.buyers,
        rejectors: globalSimulationStats.rejectors,
        waiting: globalSimulationStats.waiting,
    };
}

function stepDay() {
    const price = Number(simScenario?.price?.value) || 100;
    
    // Fetch the pre-calculated tensor states for this day (0-indexed)
    const dayStates = simulationHistory[currentDay - 1] || [];

    let b = 0, r = 0, w = 0;
    if (dayStates.length > 0) {
        for (let i = 0; i < dayStates.length; i++) {
            if (dayStates[i] === 1) b++;
            else if (dayStates[i] === -1) r++;
            else w++;
        }
    } else {
        w = totalPopSize;
    }
    
    globalSimulationStats = { buyers: b, rejectors: r, waiting: w, total: totalPopSize };

    nodes.forEach((n) => {
        const s = dayStates[n.id] || 0;
        if (s === 1) n.state = 'state-buy';
        else if (s === -1) n.state = 'state-reject';
        else n.state = 'state-wait';
    });

    // Derive seed from scenario so events vary per product (deterministic but scenario-unique)
    const scenarioSeed = (() => {
        const key = `${simScenario?.product_name?.value || ''}${simScenario?.price?.value || ''}${simScenario?.category?.value || ''}`;
        let h = 0;
        for (let i = 0; i < key.length; i++) { h = Math.imul(31, h) + key.charCodeAt(i) | 0; }
        return (h >>> 0) || 42;
    })();
    checkNarrativeEvents(currentDay, simScenario, scenarioSeed);

    refreshNodeStyles();
    updateCharts(globalSimulationStats, currentDay, price);

    // Update progress bar and day counter
    const progress = document.getElementById('timeline-progress');
    const dayDisplay = document.getElementById('timeline-day-display');
    if (progress) progress.style.width = `${(currentDay / 30) * 100}%`;
    if (dayDisplay) dayDisplay.textContent = `Day ${currentDay} / 30`;

    document.dispatchEvent(new CustomEvent('simulation-step', { detail: { day: currentDay } }));
    currentDay++;
}

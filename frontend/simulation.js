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

export async function initSimulation(scenario, onNodeClick) {
    simScenario = scenario;
    currentDay = 1;
    isRunning = false;
    clearInterval(intervalId);

    // Re-generate scenario-specific agents locally (to keep graph visual layout)
    initData(scenario);

    // Reset all nodes to wait state
    nodes.forEach(n => { n.state = 'state-wait'; });
    refreshNodeStyles();
    
    // Call the PyTorch backend to pre-calculate the 30-day simulation tensor
    const payload = {
        price: Number(scenario?.price?.value) || 100,
        marketing_budget: Number(scenario?.marketing_budget?.value) || 500000,
        agents: nodes,
        links: links
    };
    
    try {
        console.log("[Simulyn] Calling PyTorch Neural Economic Engine...");
        const res = await runSimulation(payload);
        simulationHistory = res.history || [];
        console.log(`[Simulyn] Received simulation tensor using device: ${res.device}`);
    } catch (e) {
        console.error("[Simulyn] PyTorch engine error (fallback to blank):", e);
        // Fallback: 30 days of just waiting
        simulationHistory = Array.from({length: 30}, () => Array(300).fill(0));
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
        buyers: nodes.filter(n => n.state === 'state-buy').length,
        rejectors: nodes.filter(n => n.state === 'state-reject').length,
        waiting: nodes.filter(n => n.state === 'state-wait').length,
    };
}

function stepDay() {
    const price = Number(simScenario?.price?.value) || 100;
    
    // Fetch the pre-calculated tensor states for this day (0-indexed)
    const dayStates = simulationHistory[currentDay - 1] || [];

    nodes.forEach((n, idx) => {
        const s = dayStates[idx] || 0;
        if (s === 1) n.state = 'state-buy';
        else if (s === -1) n.state = 'state-reject';
        else n.state = 'state-wait';
    });

    // We still check narrative events to display them in the UI timeline
    checkNarrativeEvents(currentDay, simScenario, 42); // fixed seed for visual consistency

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

// =============================================
// timeline.js — Timeline engine controls
// =============================================

import { startSimulation, pauseSimulation, setPlaybackSpeed } from './simulation.js';

export function initTimeline(onSimulationComplete) {
    const playBtn = document.getElementById('timeline-play');
    const pauseBtn = document.getElementById('timeline-pause');
    const speedSelect = document.getElementById('timeline-speed');

    if (playBtn) playBtn.addEventListener('click', () => startSimulation(onSimulationComplete));
    if (pauseBtn) pauseBtn.addEventListener('click', () => pauseSimulation());
    if (speedSelect) speedSelect.addEventListener('change', e => setPlaybackSpeed(parseInt(e.target.value)));
}

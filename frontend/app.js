// =============================================
// app.js — Main orchestrator. Wires everything together.
// =============================================

import { initGraph, rebuildGraph } from './graph.js';
import { initCharts, resetCharts } from './charts.js';
import { initTimeline } from './timeline.js';
import { initUI, transitionToWorkspace, showNavReportButton, showToast } from './ui.js';
import { extractScenario, runBenchmark } from './api.js';
import { renderBusinessBrief, renderAssumptionsPanel } from './businessBrief.js';
import { handleNodeClick } from './entityInspector.js';
import { initSimulation, startSimulation } from './simulation.js';
import { showExecutiveReport, exportPDF } from './report.js';

let currentScenarioData = null;
let graphInitialized = false;

document.addEventListener('DOMContentLoaded', () => {

    // Initialize charts only (no agent data yet — waits for scenario)
    initCharts();
    initTimeline(() => {
        // Simulation complete → show report automatically
        showNavReportButton(() => showExecutiveReport(currentScenarioData));
        setTimeout(() => showExecutiveReport(currentScenarioData), 800);
        showToast('Simulation complete! Executive Report is ready.', 'success');
    });

    // Wire UI events
    initUI(async (scenarioText) => {
        await processScenario(scenarioText);
    });

    // PDF Export button in modal
    const exportBtn = document.getElementById('export-pdf-btn');
    if (exportBtn) exportBtn.addEventListener('click', () => exportPDF());

    // GPU Benchmark modal
    initBenchmarkModal();
});

async function processScenario(scenarioText) {
    // Optimistic transition to workspace
    transitionToWorkspace('Analyzing...');

    // Show extraction progress in brief panel
    const briefContainer = document.getElementById('business-brief-content');
    const steps = ['Parsing scenario text...', 'Extracting parameters...', 'Calibrating agent population...', 'Preparing simulation...'];
    let stepIdx = 0;
    
    if (briefContainer) {
        const showStep = () => {
            briefContainer.innerHTML = `
                <div class="space-y-3">
                    ${[...Array(4)].map((_, i) => `
                    <div class="brief-field" style="animation-delay:${i * 0.08}s;">
                        <div class="h-2 bg-[#1e2332] rounded animate-pulse mb-1 w-1/3"></div>
                        <div class="h-3 bg-[#1e2332] rounded animate-pulse w-full"></div>
                    </div>`).join('')}
                </div>
                <div class="mt-3 flex items-center gap-2 text-[11px] text-accent">
                    <div class="w-3 h-3 border border-accent border-t-transparent rounded-full animate-spin"></div>
                    <span>${steps[stepIdx] || 'Processing...'}</span>
                </div>`;
        };
        showStep();
        const stepInterval = setInterval(() => {
            stepIdx = Math.min(stepIdx + 1, steps.length - 1);
            showStep();
        }, 1200);

        try {
            // Call AI extraction
            const data = await extractScenario(scenarioText);
            clearInterval(stepInterval);
            currentScenarioData = data;

            // Update nav with real product name
            const navLabel = document.getElementById('nav-product-label');
            if (navLabel) navLabel.textContent = data.product_name?.value || 'Simulation';

            // Render brief + assumptions
            renderBusinessBrief(data);
            renderAssumptionsPanel(data);

            // Initialize D3 graph with scenario-specific agents AFTER workspace is visible
            if (!graphInitialized) {
                setTimeout(() => {
                    initGraph((nodeData) => handleNodeClick(nodeData, currentScenarioData));
                    graphInitialized = true;
                }, 400);
            } else {
                // Rebuild graph with new scenario data (new agent population)
                setTimeout(() => {
                    rebuildGraph(data, (nodeData) => handleNodeClick(nodeData, currentScenarioData));
                    resetCharts();
                }, 400);
            }

            // Initialize scenario-specific simulation (also re-generates agents)
            initSimulation(data, (nodeData) => handleNodeClick(nodeData, currentScenarioData));

            // Auto-start simulation after brief delay
            const product = data.product_name?.value || 'product';
            const confidence = data.overall_confidence || '90%';
            showToast(`"${product}" extracted with ${confidence} confidence — starting simulation`, 'success');

            setTimeout(() => {
                startSimulation(() => {
                    showNavReportButton(() => showExecutiveReport(currentScenarioData));
                    setTimeout(() => showExecutiveReport(currentScenarioData), 600);
                    showToast('Simulation complete! Executive Report ready.', 'success');
                });
            }, 800);

        } catch (err) {
            clearInterval(stepInterval);
            console.error('[Simulyn] Scenario error:', err);
            if (briefContainer) {
                briefContainer.innerHTML = `
                    <div class="text-[12px] text-danger">
                        <div class="font-semibold mb-1">Extraction failed</div>
                        <div class="text-muted">Could not reach the AI engine. Check the backend is running on port 8000.</div>
                    </div>`;
            }
            showToast('Backend not responding. Start it with run.bat', 'danger');
        }
    }
}

function initBenchmarkModal() {
    const openBtn = document.getElementById('gpu-benchmark-btn');
    const closeBtn = document.getElementById('close-benchmark-btn');
    const modal = document.getElementById('benchmark-modal');
    const runBtn = document.getElementById('run-benchmark-btn');
    const runLabel = document.getElementById('run-benchmark-label');
    const sizeButtons = document.querySelectorAll('.benchmark-size-btn');
    let selectedNodes = 1000;

    // Open/close modal
    openBtn?.addEventListener('click', () => {
        modal?.classList.replace('hidden', 'flex');
    });
    closeBtn?.addEventListener('click', () => {
        modal?.classList.replace('flex', 'hidden');
    });
    modal?.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.replace('flex', 'hidden');
    });

    // Size selector
    sizeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            sizeButtons.forEach(b => {
                b.classList.remove('active-size', 'text-white', 'bg-accent/20', 'border-accent/30');
                b.classList.add('text-muted', 'border-[#1e2332]');
            });
            btn.classList.add('active-size', 'text-white', 'bg-accent/20', 'border-accent/30');
            btn.classList.remove('text-muted', 'border-[#1e2332]');
            selectedNodes = parseInt(btn.dataset.nodes);
        });
    });

    // Run benchmark
    runBtn?.addEventListener('click', async () => {
        if (runLabel) runLabel.textContent = 'Running…';
        if (runBtn) runBtn.disabled = true;

        const resultsEl = document.getElementById('benchmark-results');
        const cpuEl = document.getElementById('bm-cpu-time');
        const gpuEl = document.getElementById('bm-gpu-time');
        const speedupRow = document.getElementById('bm-speedup-row');
        const speedupEl = document.getElementById('bm-speedup');
        const noGpuEl = document.getElementById('bm-no-gpu-note');

        try {
            const data = await runBenchmark(selectedNodes);
            resultsEl?.classList.remove('hidden');
            speedupRow?.classList.add('hidden');
            noGpuEl?.classList.add('hidden');

            const cpuMs = typeof data.cpu_time_sec === 'number'
                ? `${(data.cpu_time_sec * 1000).toFixed(1)} ms`
                : (data.cpu_time_sec || 'N/A');
            if (cpuEl) cpuEl.textContent = cpuMs;

            if (data.hardware_accelerated && typeof data.gpu_time_sec === 'number') {
                const gpuMs = `${(data.gpu_time_sec * 1000).toFixed(1)} ms`;
                if (gpuEl) gpuEl.textContent = gpuMs;
                const speedup = (data.cpu_time_sec / data.gpu_time_sec).toFixed(1);
                if (speedupEl) speedupEl.textContent = `${speedup}×`;
                speedupRow?.classList.remove('hidden');
            } else {
                if (gpuEl) gpuEl.textContent = 'N/A';
                noGpuEl?.classList.remove('hidden');
            }
            showToast('Benchmark complete!', 'success');
        } catch (err) {
            showToast('Benchmark failed — is the backend running?', 'danger');
        } finally {
            if (runLabel) runLabel.textContent = 'Run Benchmark';
            if (runBtn) runBtn.disabled = false;
        }
    });
}

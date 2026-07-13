// =============================================
// app.js — Main orchestrator. Wires everything together.
// =============================================

import { initGraph, rebuildGraph } from './graph.js';
import { initCharts, resetCharts } from './charts.js';
import { initTimeline } from './timeline.js';
import { initUI, transitionToWorkspace, showNavReportButton, showToast, checkBackendStatus } from './ui.js';
import { extractScenario, runBenchmark, generatePopulation } from './api.js';
import { renderBusinessBrief, renderAssumptionsPanel } from './businessBrief.js';
import { handleNodeClick } from './entityInspector.js';
import { initSimulation, startSimulation } from './simulation.js';
import { showExecutiveReport, exportPDF } from './report.js';

let currentScenarioData = null;
let graphInitialized = false;

document.addEventListener('DOMContentLoaded', () => {

    // Check if backend is reachable on load — updates "Engine Online" indicator
    checkBackendStatus();

    // Initialize charts only (no agent data yet — waits for scenario)
    initCharts();
    initTimeline(() => {
        // Simulation complete → show report automatically
        showNavReportButton(() => showExecutiveReport(currentScenarioData));
        showExecutiveReport(currentScenarioData);
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

// --- Execution Timeline & Ghost Canvas Logic ---
let ghostAnimFrame = null;

function initGhostGraph() {
    const canvas = document.getElementById('ghost-canvas');
    if (!canvas) return;
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    const ctx = canvas.getContext('2d');
    canvas.style.opacity = '1';

    const particles = Array.from({ length: 150 }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1
    }));

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'rgba(99, 102, 241, 0.4)';
        ctx.strokeStyle = 'rgba(99, 102, 241, 0.1)';
        
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();

            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                if (dist < 100) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
        ghostAnimFrame = requestAnimationFrame(draw);
    }
    draw();
}

function stopGhostGraph() {
    const canvas = document.getElementById('ghost-canvas');
    if (canvas) canvas.style.opacity = '0';
    if (ghostAnimFrame) {
        setTimeout(() => cancelAnimationFrame(ghostAnimFrame), 1000);
    }
}

function appendLog(message, type = 'pending') {
    const logs = document.getElementById('execution-logs');
    if (!logs) return;
    const div = document.createElement('div');
    div.className = `log-line log-${type}`;
    div.innerHTML = type === 'success' ? `✓ ${message}` : message;
    logs.appendChild(div);
    logs.scrollTop = logs.scrollHeight;
}

async function processScenario(scenarioText) {
    // Optimistic transition to workspace
    transitionToWorkspace('Initializing Engine...');
    
    const overlay = document.getElementById('execution-timeline-overlay');
    const logs = document.getElementById('execution-logs');
    if (overlay) overlay.classList.replace('hidden', 'flex');
    if (logs) logs.innerHTML = '';

    const briefContainer = document.getElementById('business-brief-content');
    
    if (briefContainer) {
        briefContainer.innerHTML = `
            <div class="space-y-3">
                <div class="brief-field"><div class="h-2 bg-[#1e2332] rounded animate-pulse mb-1 w-1/3"></div><div class="h-3 bg-[#1e2332] rounded animate-pulse w-full"></div></div>
                <div class="brief-field"><div class="h-2 bg-[#1e2332] rounded animate-pulse mb-1 w-1/3"></div><div class="h-3 bg-[#1e2332] rounded animate-pulse w-full"></div></div>
            </div>`;

        try {
            initGhostGraph();
            appendLog('Scenario received. Establishing API connection...', 'active');
            appendLog('Classifying product and target audience...', 'pending');
            
            const data = await extractScenario(scenarioText);
            
            appendLog('Product classified.', 'success');
            appendLog('Industry identified.', 'success');
            
            currentScenarioData = data;
            const navLabel = document.getElementById('nav-product-label');
            if (navLabel) navLabel.textContent = data.product_name?.value || 'Simulation';

            appendLog('Generating SKPI behavioral archetypes...', 'active');
            
            const popData = await generatePopulation(data, 300);
            
            appendLog('Archetypes generation complete.', 'success');
            appendLog('Building synthetic population (300 nodes)...', 'success');
            appendLog('Generating social network edges...', 'success');

            renderBusinessBrief(data);
            renderAssumptionsPanel(data);

            appendLog('Initializing D3 Graph Layout...', 'active');

            if (!graphInitialized) {
                initGraph((nodeData) => handleNodeClick(nodeData, currentScenarioData), popData);
                graphInitialized = true;
            } else {
                rebuildGraph(data, (nodeData) => handleNodeClick(nodeData, currentScenarioData), popData);
                resetCharts();
            }

            stopGhostGraph();
            
            appendLog('Graph initialized.', 'success');
            appendLog('Computing PyTorch Tensor Matrices...', 'active');

            await initSimulation(data, popData);
            
            appendLog('PyTorch Tensors computed.', 'success');
            appendLog('Market simulation ready.', 'success');

            const product = data.product_name?.value || 'product';
            showToast(`"${product}" generated — starting PyTorch simulation`, 'success');

            // Hide overlay after delay
            setTimeout(() => {
                if (overlay) overlay.classList.replace('flex', 'hidden');
            }, 1500);

            // Start simulation immediately
            startSimulation(() => {
                showNavReportButton(() => showExecutiveReport(currentScenarioData));
                showExecutiveReport(currentScenarioData);
                showToast('Simulation complete! Executive Report ready.', 'success');
            });

        } catch (err) {
            console.error('[Simulyn] Scenario error:', err);
            stopGhostGraph();
            appendLog('Engine Fault: API connection failed.', 'danger');
            if (briefContainer) {
                briefContainer.innerHTML = `
                    <div class="text-[12px] text-danger">
                        <div class="font-semibold mb-1">Extraction failed</div>
                        <div class="text-muted">Could not reach the AI engine. Check the backend is running.</div>
                    </div>`;
            }
            showToast('Backend not responding. Is the server running?', 'danger');
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

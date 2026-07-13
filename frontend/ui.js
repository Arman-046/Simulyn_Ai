// =============================================
// ui.js — All UI interactions, transitions, file uploads
// =============================================

const TEMPLATES = {
    hardware: "Product: Revolutionary AI Medical Scanner\nTarget Audience: Private Hospitals & Clinics\nPrice: $200 (Mass Market)\nMarketing Budget: $10,000,000\nLaunch Region: Global\nUSP: Detects anomalies with 99.9% accuracy instantly, massively undercutting competitor pricing while offering superior technology.",
    saas: "Product: Flimsy Plastic Straw\nTarget Audience: Eco-conscious Gen Z consumers\nPrice: $50 (Premium)\nMarketing Budget: $100\nLaunch Region: California\nUSP: A standard single-use plastic straw marketed as a luxury item.",
    retail: "Product: Mid-range Electric Scooter\nTarget Audience: Urban commuters aged 18-35\nPrice: $600 (Mid-Market)\nMarketing Budget: $500,000\nLaunch Region: Europe\nUSP: Foldable design with a 20-mile range and standard safety features. Competes with Xiaomi and Segway."
};

export function initUI(onProcessScenario) {
    const input = document.getElementById('scenario-input');
    const sendBtn = document.getElementById('send-scenario-btn');
    const txtBtn = document.getElementById('btn-upload-txt');
    const pdfBtn = document.getElementById('btn-upload-pdf');
    const docxBtn = document.getElementById('btn-upload-docx');
    const closeReportBtn = document.getElementById('close-report-btn');

    // === Send button ===
    if (sendBtn) {
        sendBtn.addEventListener('click', () => {
            const val = input?.value?.trim();
            if (!val || val.length < 15) {
                flashInputError(input, 'Please add more detail about price, product, and target audience.');
                return;
            }
            onProcessScenario(val);
        });
    }

    // === Keyboard shortcut: Ctrl+Enter to submit ===
    if (input) {
        input.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') sendBtn?.click();
        });
    }

    // === Template cards ===
    document.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('click', () => {
            const key = card.dataset.template;
            if (input && TEMPLATES[key]) {
                input.value = TEMPLATES[key];
                input.focus();
                sendBtn?.click();
            }
        });
    });

    // === TXT upload ===
    if (txtBtn) {
        txtBtn.addEventListener('click', () => {
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.txt';
            fileInput.onchange = e => {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = ev => {
                    if (input) {
                        input.value = ev.target.result.slice(0, 2000); // Limit to 2000 chars
                        txtBtn.textContent = '✓ TXT Loaded';
                        setTimeout(() => { txtBtn.innerHTML = `<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>TXT`; }, 2000);
                    }
                };
                reader.readAsText(file);
            };
            fileInput.click();
        });
    }

    // === Coming Soon documents — visually labeled as Pro feature ===
    pdfBtn?.addEventListener('click', () => showToast('PDF & DOCX import is a Pro feature — coming soon.', 'info'));
    docxBtn?.addEventListener('click', () => showToast('PDF & DOCX import is a Pro feature — coming soon.', 'info'));

    // === Report modal close ===
    if (closeReportBtn) {
        closeReportBtn.addEventListener('click', () => {
            const modal = document.getElementById('report-modal');
            if (modal) { modal.style.opacity = '0'; setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); modal.style.opacity = ''; }, 300); }
        });
    }
}

// === Live Backend Health Check ===
export async function checkBackendStatus() {
    const statusEl = document.getElementById('system-status');
    const API_BASE = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')
        ? 'http://127.0.0.1:8000/api'
        : '/api';
    try {
        const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(4000) });
        const data = await res.json();
        if (statusEl) {
            const gpuNote = data.pytorch_installed ? ' · PyTorch Ready' : '';
            statusEl.innerHTML = `<span class="w-1.5 h-1.5 bg-success rounded-full"></span> Engine Online${gpuNote}`;
            statusEl.className = 'text-[11px] font-mono text-success flex items-center gap-1.5';
        }
    } catch (e) {
        if (statusEl) {
            statusEl.innerHTML = `<span class="w-1.5 h-1.5 bg-danger rounded-full animate-pulse"></span> Backend Offline`;
            statusEl.className = 'text-[11px] font-mono text-danger flex items-center gap-1.5';
        }
    }
}

// === Transition: Welcome → Workspace ===
export function transitionToWorkspace(productName) {
    const welcome = document.getElementById('welcome-screen');
    const workspace = document.getElementById('workspace');
    const leftPanel = document.getElementById('left-panel');
    const rightPanel = document.getElementById('right-panel');
    const navControls = document.getElementById('nav-simulation-controls');
    const navLabel = document.getElementById('nav-product-label');

    if (!welcome || !workspace) return;

    // Update nav
    if (navLabel) navLabel.textContent = productName || 'Simulation Active';
    if (navControls) navControls.classList.replace('hidden', 'flex');

    // Fade out welcome
    welcome.style.opacity = '0';
    welcome.style.transform = 'scale(0.98)';
    setTimeout(() => {
        welcome.classList.add('hidden');
        workspace.classList.replace('hidden', 'flex');
        workspace.style.opacity = '0';

        requestAnimationFrame(() => {
            workspace.style.transition = 'opacity 0.4s ease';
            workspace.style.opacity = '1';

            // Animate panels in
            if (leftPanel) {
                leftPanel.style.transition = 'opacity 0.5s ease, transform 0.5s cubic-bezier(0.16,1,0.3,1)';
                setTimeout(() => { leftPanel.style.opacity = '1'; leftPanel.style.transform = 'translateX(0)'; }, 100);
            }
            if (rightPanel) {
                rightPanel.style.transition = 'opacity 0.5s ease, transform 0.5s cubic-bezier(0.16,1,0.3,1)';
                setTimeout(() => { rightPanel.style.opacity = '1'; rightPanel.style.transform = 'translateX(0)'; }, 200);
            }
        });
    }, 400);
}

// === Show nav report button ===
export function showNavReportButton(onShowReport) {
    const btn = document.getElementById('nav-report-btn');
    if (btn) {
        btn.classList.remove('hidden');
        btn.addEventListener('click', onShowReport);
    }
}

// === Toast notifications ===
export function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    const colors = { success: 'bg-success text-black', danger: 'bg-danger text-white', info: 'bg-accent text-white', warning: 'bg-warning text-black' };
    toast.className = `fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] px-5 py-2.5 rounded-xl text-sm font-semibold shadow-2xl ${colors[type] || colors.info} transition-all duration-300`;
    toast.style.opacity = '0'; toast.style.transform = 'translate(-50%, 8px)';
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => { toast.style.opacity = '1'; toast.style.transform = 'translate(-50%, 0)'; });
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3500);
}

function flashInputError(input, message) {
    if (!input) return;
    input.style.borderColor = '#ef4444';
    showToast(message, 'danger');
    setTimeout(() => { input.style.borderColor = ''; }, 2000);
}

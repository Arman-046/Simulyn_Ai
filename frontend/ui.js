// =============================================
// ui.js — All UI interactions, transitions, file uploads
// =============================================

const TEMPLATES = {
    hardware: "We are launching AI-powered Smart Glasses in the US for $999, targeting tech professionals aged 25–45 with a $2M marketing budget. Key features include AR overlays, 4K camera, and 12-hour battery. Competitors include Meta Ray-Ban and Apple Vision Pro.",
    saas: "We are changing our B2B project management SaaS pricing from $10 per user/month to $18 per user/month. We have 50,000 active users, primarily startup founders and product managers in North America. Marketing budget is $500K.",
    retail: "We are opening 5 premium coffee shops in London, UK. Target audience is professionals aged 28–50. Pricing is £7 for a specialty drink. Initial investment is £2M. We will compete with Starbucks and independent artisan cafes."
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

    // === Coming Soon documents ===
    const comingSoon = () => showToast('PDF & DOCX support is coming in Enterprise Edition.', 'info');
    pdfBtn?.addEventListener('click', comingSoon);
    docxBtn?.addEventListener('click', comingSoon);

    // === Report modal close ===
    if (closeReportBtn) {
        closeReportBtn.addEventListener('click', () => {
            const modal = document.getElementById('report-modal');
            if (modal) { modal.style.opacity = '0'; setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); modal.style.opacity = ''; }, 300); }
        });
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

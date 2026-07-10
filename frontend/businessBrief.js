// =============================================
// businessBrief.js — AI Business Brief & Assumptions rendering
// =============================================

export function renderBusinessBrief(data) {
    const briefContainer = document.getElementById('business-brief-content');
    const productName = document.getElementById('brief-product-name');
    const confidenceBadge = document.getElementById('brief-confidence-badge');
    const confidenceValue = document.getElementById('brief-confidence-value');

    if (productName) productName.textContent = data.product_name?.value || 'Unknown Product';
    if (confidenceBadge && data.overall_confidence) {
        confidenceBadge.classList.remove('hidden');
        if (confidenceValue) confidenceValue.textContent = data.overall_confidence;
    }

    if (!briefContainer) return;

    const fields = [
        { label: 'Industry', value: data.industry?.value, conf: data.industry?.confidence },
        { label: 'Target Audience', value: data.target_audience?.value, conf: data.target_audience?.confidence },
        { label: 'Price', value: data.price?.value ? `${data.currency?.value || '$'}${data.price.value.toLocaleString()}` : null, conf: data.price?.confidence },
        { label: 'Region', value: data.launch_region?.value, conf: data.launch_region?.confidence },
        { label: 'Business Model', value: data.business_model?.value, conf: data.business_model?.confidence },
        { label: 'Competitors', value: data.competitors?.value, conf: data.competitors?.confidence },
        { label: 'Key Risks', value: data.risks?.value, isRisk: true },
        { label: 'USP', value: data.usp?.value },
    ];

    briefContainer.innerHTML = '';
    fields.forEach((f, i) => {
        if (!f.value) return;
        const div = document.createElement('div');
        div.className = 'brief-field';
        div.style.animationDelay = `${i * 0.08}s`;
        div.innerHTML = `
            <div class="text-[10px] text-muted uppercase tracking-widest mb-0.5">${f.label}</div>
            <div class="flex items-center justify-between gap-2">
                <div class="text-[12px] ${f.isRisk ? 'text-warning' : 'text-white'} font-medium leading-snug">${f.value}</div>
                ${f.conf ? `<span class="text-[10px] text-success shrink-0">${f.conf}</span>` : ''}
            </div>`;
        briefContainer.appendChild(div);
    });
}

export function renderAssumptionsPanel(data) {
    const container = document.getElementById('assumptions-content');
    if (!container) return;

    const marketBudget = data.marketing_budget?.value;
    const supplyCapacity = data.supply_capacity?.value;

    container.innerHTML = `
        <ul class="space-y-2">
            <li class="flex justify-between text-[11px]"><span class="text-muted">Demand Growth</span><span class="text-white font-medium">3% baseline</span></li>
            <li class="flex justify-between text-[11px]"><span class="text-muted">Inflation Factor</span><span class="text-white font-medium">2%</span></li>
            <li class="flex justify-between text-[11px]"><span class="text-muted">Competitor Response</span><span class="text-white font-medium">Aggressive</span></li>
            <li class="flex justify-between text-[11px]"><span class="text-muted">Supply Chain</span><span class="text-white font-medium">${supplyCapacity || 'Stable'}</span></li>
            <li class="flex justify-between text-[11px]"><span class="text-muted">Marketing Budget</span><span class="text-white font-medium">${marketBudget ? '$' + Number(marketBudget).toLocaleString() : 'Standard'}</span></li>
            <li class="flex justify-between text-[11px]"><span class="text-muted">Simulation Agents</span><span class="text-white font-medium">300 synthetic</span></li>
            <li class="flex justify-between text-[11px]"><span class="text-muted">Time Horizon</span><span class="text-white font-medium">30 days</span></li>
        </ul>`;
}

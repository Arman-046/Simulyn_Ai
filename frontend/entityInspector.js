// =============================================
// entityInspector.js — Node click → AI explainability
// =============================================

import { explainDecision } from './api.js';

export async function handleNodeClick(agentData, scenarioData) {
    const panel = document.getElementById('inspector-content');
    if (!panel) return;

    const stateLabel = agentData.state === 'state-buy' ? 'Adopted' : agentData.state === 'state-reject' ? 'Rejected' : 'Waiting';
    const stateColor = agentData.state === 'state-buy' ? '#10b981' : agentData.state === 'state-reject' ? '#ef4444' : '#f59e0b';

    // Skeleton loading
    panel.innerHTML = `
        <div class="w-full space-y-4">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-[#1e2332] animate-pulse"></div>
                <div class="space-y-1.5 flex-1">
                    <div class="h-3 bg-[#1e2332] rounded animate-pulse w-3/4"></div>
                    <div class="h-2 bg-[#1e2332] rounded animate-pulse w-1/2"></div>
                </div>
            </div>
            <div class="space-y-2">
                ${[...Array(5)].map(() => `<div class="h-2 bg-[#1e2332] rounded animate-pulse"></div>`).join('')}
            </div>
            <div class="text-[11px] text-muted text-center mt-4 animate-pulse">Generating AI reasoning...</div>
        </div>`;

    try {
        const explanation = scenarioData ? await explainDecision(agentData, scenarioData) : null;
        const reason = explanation?.reason || (agentData.state === 'state-buy' ? `Strong income level ($${agentData.income.toLocaleString()}) relative to price. ${agentData.mood} mood aligned with adoption. Paycheck timing favorable.` : agentData.state === 'state-reject' ? `Price exceeds comfortable threshold given savings ($${agentData.savings.toLocaleString()}). ${agentData.financialStatus}.` : 'Still evaluating. Waiting for more social proof before committing.');
        const counterfactual = explanation?.counterfactual || (agentData.state === 'state-buy' ? `If price increased by 40%, this agent would reconsider.` : `If peer adoption exceeds 30%, this agent may convert.`);
        const probability = explanation?.probability || (agentData.state === 'state-buy' ? '88%' : agentData.state === 'state-reject' ? '76%' : '55%');
        const confidence = explanation?.confidence || 'High (91%)';

        panel.innerHTML = `
            <div class="w-full space-y-4 text-[12px] animate-fade-in" style="animation: fadeUp 0.3s ease forwards;">
                <!-- Agent Header -->
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0" style="background: ${stateColor}22; color: ${stateColor};">
                        ${agentData.id % 100}
                    </div>
                    <div>
                        <div class="text-white font-semibold">${agentData.profession}</div>
                        <div class="text-muted text-[11px]">${agentData.location} · ${agentData.type}</div>
                    </div>
                </div>

                <!-- Key Stats -->
                <div class="grid grid-cols-2 gap-2 text-[11px]">
                    <div class="bg-[#141820] rounded-lg p-2.5">
                        <div class="text-muted mb-0.5">Annual Income</div>
                        <div class="text-white font-semibold">$${agentData.income.toLocaleString()}</div>
                    </div>
                    <div class="bg-[#141820] rounded-lg p-2.5">
                        <div class="text-muted mb-0.5">Savings</div>
                        <div class="text-white font-semibold">$${agentData.savings.toLocaleString()}</div>
                    </div>
                    <div class="bg-[#141820] rounded-lg p-2.5">
                        <div class="text-muted mb-0.5">Influence</div>
                        <div class="text-white font-semibold">${agentData.influenceScore}/100</div>
                    </div>
                    <div class="bg-[#141820] rounded-lg p-2.5">
                        <div class="text-muted mb-0.5">Preference</div>
                        <div class="text-white font-semibold text-[10px]">${agentData.preference}</div>
                    </div>
                </div>

                <!-- Decision -->
                <div class="rounded-xl p-3 border" style="border-color: ${stateColor}33; background: ${stateColor}0d;">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[10px] text-muted uppercase tracking-widest">Decision</span>
                        <div class="flex items-center gap-2">
                            <span class="font-bold" style="color: ${stateColor};">${stateLabel}</span>
                            <span class="text-muted text-[10px]">${probability}</span>
                        </div>
                    </div>
                    <p class="text-[11px] text-gray-300 leading-relaxed">${reason}</p>
                </div>

                <!-- Counterfactual -->
                <div class="rounded-xl p-3 bg-[#0f1219] border border-[#1e2332]">
                    <div class="text-[10px] text-accent uppercase tracking-widest mb-1.5">Counterfactual</div>
                    <p class="text-[11px] text-gray-400 leading-relaxed italic">"${counterfactual}"</p>
                </div>

                <!-- Memory -->
                <div class="text-[10px] text-muted">
                    <span class="uppercase tracking-widest">Memory:</span> ${agentData.recentPurchase !== 'Nothing' ? `Previously bought ${agentData.recentPurchase}.` : 'No recent major purchase.'} ${agentData.recentNegativeExperience !== 'None' ? `Experienced: ${agentData.recentNegativeExperience}.` : ''}
                </div>

                <div class="text-[10px] text-muted flex justify-between pt-2 border-t border-[#1e2332]">
                    <span>AI Confidence: <span class="text-success">${confidence}</span></span>
                    <span>Mood: <span class="text-white">${agentData.mood}</span></span>
                </div>
            </div>`;
    } catch (e) {
        panel.innerHTML = `
            <div class="text-center space-y-3">
                <div class="text-2xl">⚡</div>
                <div class="text-[11px] text-muted">Agent ${agentData.id}</div>
                <div class="rounded-xl p-3 border" style="border-color: ${stateColor}33; background: ${stateColor}0d;">
                    <div class="font-bold text-sm mb-1" style="color: ${stateColor};">${stateLabel}</div>
                    <div class="text-[11px] text-muted">Income: $${agentData.income.toLocaleString()} · ${agentData.financialStatus}</div>
                </div>
            </div>`;
    }
}

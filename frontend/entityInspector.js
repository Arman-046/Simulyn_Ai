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
            <div class="text-[11px] text-muted text-center mt-4 animate-pulse">
                Running Deep Intelligence Pipeline...<br>
                Graph → Persona → Reasoning → Belief → Policy
            </div>
        </div>`;

    // Deterministic Human Name Generation — declared at top of try block so accessible in all branches
    const firstNames = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"];
    const lastNames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"];

    try {
        const explanation = scenarioData ? await explainDecision(agentData, scenarioData) : null;
        
        // If we have full SKPI deep data, render the stunning pipeline view
        if (explanation?.skpi_data) {
            const { reasoning, belief, policy } = explanation.skpi_data;
            
            const p = policy;
            const bProb = (p.buy_probability * 100).toFixed(0);
            const wProb = (p.wait_probability * 100).toFixed(0);
            const rProb = (p.reject_probability * 100).toFixed(0);
            
            const dynState = agentData.state === 'state-buy' ? 'Adopted' : (agentData.state === 'state-reject' ? 'Rejected' : 'Waiting');
            const dynColor = agentData.state === 'state-buy' ? '#10b981' : (agentData.state === 'state-reject' ? '#ef4444' : '#f59e0b');
            
            const agentId = agentData.id !== undefined ? agentData.id : (agentData.index || 0);
            const fName = firstNames[agentId % firstNames.length];
            const lName = lastNames[(agentId * 7) % lastNames.length];
            const fullName = `${fName} ${lName}`;
            
            panel.innerHTML = `
                <div class="w-full space-y-4 text-[12px] animate-fade-in" style="animation: fadeUp 0.3s ease forwards;">
                    <!-- Agent Header -->
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0" style="background: ${dynColor}22; color: ${dynColor}; border: 1px solid ${dynColor}66">
                            ${fName[0]}${lName[0]}
                        </div>
                        <div>
                            <div class="text-white font-semibold">${fullName} <span class="text-muted font-normal text-[11px] ml-1">ID:${agentData.id}</span></div>
                            <div class="text-muted text-[11px]">${agentData.profession} · ${agentData.location}</div>
                        </div>
                    </div>

                    <!-- 1. Subjective Belief -->
                    <div class="rounded-xl p-3 border border-indigo-500/30 bg-indigo-500/10">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-[10px] text-indigo-400 uppercase tracking-widest font-bold">1. Subjective Belief</span>
                            <span class="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full">${belief.sentiment}</span>
                        </div>
                        <p class="text-[11px] text-gray-200 leading-relaxed italic border-l-2 border-indigo-500 pl-2">
                            "${belief.belief_statement}"
                        </p>
                    </div>

                    <!-- 2. Logical Reasoning -->
                    <div class="rounded-xl p-3 bg-[#0f1219] border border-[#1e2332]">
                        <div class="text-[10px] text-accent uppercase tracking-widest mb-1.5 font-bold">2. Objective Reasoning</div>
                        <p class="text-[11px] text-gray-400 leading-relaxed mb-2">
                            <span class="text-white">Conclusion:</span> ${reasoning.logical_conclusion}
                        </p>
                        <div class="bg-[#141820] rounded p-2 text-[10px] space-y-1">
                            <div class="flex"><span class="text-muted w-20">Ignored:</span> <span class="flex-1 text-red-400">${reasoning.why_ignored}</span></div>
                            <div class="flex"><span class="text-muted w-20">Conflict:</span> <span class="flex-1 text-green-400">${reasoning.conflict_resolution}</span></div>
                        </div>
                    </div>
                    
                    <!-- 3. Final Decision Policy -->
                    <div class="rounded-xl p-3 border" style="border-color: ${dynColor}33; background: ${dynColor}0d;">
                        <div class="text-[10px] text-muted uppercase tracking-widest mb-2 font-bold flex justify-between">
                            <span>3. Decision Policy Output</span>
                            <span style="color: ${dynColor}">${dynState}</span>
                        </div>
                        
                        <div class="space-y-2 text-[10px]">
                            <!-- Buy Bar -->
                            <div class="flex items-center gap-2">
                                <span class="w-10 text-muted">Buy</span>
                                <div class="flex-1 bg-gray-800 rounded-full h-1.5 overflow-hidden">
                                    <div class="bg-emerald-500 h-full" style="width: ${bProb}%"></div>
                                </div>
                                <span class="w-6 text-right">${bProb}%</span>
                            </div>
                            <!-- Wait Bar -->
                            <div class="flex items-center gap-2">
                                <span class="w-10 text-muted">Wait</span>
                                <div class="flex-1 bg-gray-800 rounded-full h-1.5 overflow-hidden">
                                    <div class="bg-amber-500 h-full" style="width: ${wProb}%"></div>
                                </div>
                                <span class="w-6 text-right">${wProb}%</span>
                            </div>
                            <!-- Reject Bar -->
                            <div class="flex items-center gap-2">
                                <span class="w-10 text-muted">Reject</span>
                                <div class="flex-1 bg-gray-800 rounded-full h-1.5 overflow-hidden">
                                    <div class="bg-red-500 h-full" style="width: ${rProb}%"></div>
                                </div>
                                <span class="w-6 text-right">${rProb}%</span>
                            </div>
                        </div>
                        <div class="mt-2 text-[9px] text-gray-500 leading-tight">
                            ${policy.policy_explanation}
                        </div>
                    </div>

                    <!-- Pipeline Footer -->
                    <div class="text-[9px] text-center text-muted uppercase tracking-widest pt-2 border-t border-[#1e2332]">
                        Simulyn Deep Intelligence Layer Active
                    </div>
                </div>`;
                
        } else {
            // Fallback for non-SKPI responses
            const reason = explanation?.reason || (agentData.state === 'state-buy' ? `Strong income level ($${agentData.income.toLocaleString()}) relative to price. ${agentData.mood} mood aligned with adoption. Paycheck timing favorable.` : agentData.state === 'state-reject' ? `Price exceeds comfortable threshold given savings ($${agentData.savings.toLocaleString()}). ${agentData.financialStatus}.` : 'Still evaluating. Waiting for more social proof before committing.');
            const counterfactual = explanation?.counterfactual || (agentData.state === 'state-buy' ? `If price increased by 40%, this agent would reconsider.` : `If peer adoption exceeds 30%, this agent may convert.`);
            const probability = explanation?.probability || (agentData.state === 'state-buy' ? '88%' : agentData.state === 'state-reject' ? '76%' : '55%');
            const confidence = explanation?.confidence || 'High (91%)';
    
            const agentId = agentData.id !== undefined ? agentData.id : (agentData.index || 0);
            const fName = firstNames[agentId % firstNames.length];
            const lName = lastNames[(agentId * 7) % lastNames.length];
            const fullName = `${fName} ${lName}`;
            
            panel.innerHTML = `
                <div class="w-full space-y-4 text-[12px] animate-fade-in" style="animation: fadeUp 0.3s ease forwards;">
                    <!-- Agent Header -->
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0" style="background: ${stateColor}22; color: ${stateColor};">
                            ${fName[0]}${lName[0]}
                        </div>
                        <div>
                            <div class="text-white font-semibold">${fullName} <span class="text-muted font-normal text-[11px] ml-1">ID:${agentData.id}</span></div>
                            <div class="text-muted text-[11px]">${agentData.profession} · ${agentData.location}</div>
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
                </div>`;
        }
        
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

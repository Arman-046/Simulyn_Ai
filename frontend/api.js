const API_BASE = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' || window.location.hostname === '[::1]' || window.location.hostname === '::1')
    ? 'http://127.0.0.1:8000/api' 
    : '/api';

export async function extractScenario(text) {
    const res = await fetch(`${API_BASE}/extract_scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error('API Error');
    return res.json();
}

export async function generatePopulation(scenarioData, numNodes = 300) {
    const res = await fetch(`${API_BASE}/generate_population`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioData, num_nodes: numNodes })
    });
    if (!res.ok) throw new Error('API Error');
    return res.json();
}

export async function explainDecision(agentData, scenarioData) {
    const res = await fetch(`${API_BASE}/generate_chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            agent_id: agentData.id,
            agent_type: agentData.type,
            mood: agentData.mood,
            income: agentData.income,
            product: scenarioData.product_name?.value || "Product",
            price: scenarioData.price?.value || 100,
            state: agentData.state.replace('state-', ''),
            goal: agentData.goal,
            savings: agentData.savings,
            financial_status: agentData.financialStatus,
            recent_purchase: agentData.recentPurchase,
            recent_negative_experience: agentData.recentNegativeExperience,
            current_need: agentData.currentNeed,
            monthly_expenses: agentData.monthlyExpenses,
            salary_day: agentData.salaryDay,
            preference: agentData.preference,
            location: agentData.location,
            profession: agentData.profession,
            influence_score: agentData.influenceScore,
            buying_power: agentData.buyingPower,
            reasoning_trace: window.reasoningTraces ? window.reasoningTraces[agentData.id] : null,
            persona_data: agentData.persona_data
        })
    });
    if (!res.ok) throw new Error('API Error');
    return res.json();
}

export async function getExecutiveReport(reportData) {
    const res = await fetch(`${API_BASE}/executive_summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportData)
    });
    if (!res.ok) throw new Error('API Error');
    return res.json();
}

export async function runBenchmark(numNodes) {
    const res = await fetch(`${API_BASE}/benchmark`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_nodes: numNodes })
    });
    if (!res.ok) throw new Error('API Error');
    return res.json();
}

export async function runSimulation(simulationId) {
    const res = await fetch(`${API_BASE}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ simulation_id: simulationId })
    });
    if (!res.ok) throw new Error('Simulation API Error');
    return res.json();
}

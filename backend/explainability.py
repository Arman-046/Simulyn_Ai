import json
from .config import FIREWORKS_API_KEY, FIREWORKS_BASE_URL, MODEL_NAME
from .models import ChatRequest


def get_local_explanation(req: ChatRequest) -> dict:
    """Generate a realistic explanation without AI based on agent attributes."""
    price = float(req.price)
    income = float(req.income)
    savings = float(req.savings)
    state = req.state

    affordability_ratio = price / (income * 0.03) if income > 0 else 999
    budget_pressure = req.monthly_expenses / (income / 12) if income > 0 else 1

    if state == "buy":
        if affordability_ratio < 0.5:
            reason = (f"{req.profession} in {req.location} with ${income:,.0f} income. "
                      f"Product at ${price:,.0f} is well within budget (only {affordability_ratio:.0%} of affordable range). "
                      f"{req.mood} mood and {req.financial_status} financial status strongly support adoption.")
        else:
            reason = (f"Despite moderate price sensitivity, this {req.profession} decided to adopt. "
                      f"Savings of ${savings:,.0f} cover the purchase. {req.mood} mood drove the decision. "
                      f"Paycheck timing ({req.salary_day}) was favorable.")
        counterfactual = f"If price exceeded ${price * 1.6:,.0f} (~60% higher), this agent would likely wait."
        probability = f"{min(97, 70 + int(30 * (1 - min(affordability_ratio, 1)))):.0f}%"
        confidence = "High (91%)"

    elif state == "reject":
        if affordability_ratio > 2:
            reason = (f"Price ${price:,.0f} is {affordability_ratio:.1f}× above what this {req.profession} "
                      f"(${income:,.0f}/yr, ${savings:,.0f} savings) can comfortably spend. "
                      f"{req.financial_status}. {req.recent_negative_experience} adds to hesitation.")
        else:
            reason = (f"Marginal rejection: {req.mood} mood and {req.financialStatus if hasattr(req, 'financialStatus') else req.financial_status} "
                      f"financial status tipped this {req.profession} against buying at ${price:,.0f}. "
                      f"Monthly expenses (${req.monthly_expenses:,.0f}) leave little discretionary room.")
        counterfactual = f"A {int((1 - 1/affordability_ratio) * 100):.0f}% price reduction or BNPL option would likely convert this agent."
        probability = f"{min(95, 60 + int(35 * min(affordability_ratio / 3, 1))):.0f}%"
        confidence = "High (88%)"

    else:  # wait
        reason = (f"Still evaluating. {req.profession} in {req.location} is waiting for salary day ({req.salary_day}) "
                  f"and more social proof. ${savings:,.0f} savings available but {req.financial_status}.")
        counterfactual = "Would adopt if peer adoption rate exceeds 30% or a time-limited discount is offered."
        probability = "45%"
        confidence = "Medium (72%)"

    decision_map = {"buy": "Adopted", "reject": "Rejected", "wait": "Waiting"}
    return {
        "decision": decision_map.get(state, "Waiting"),
        "probability": probability,
        "reason": reason,
        "confidence": confidence,
        "counterfactual": counterfactual,
        "memory": f"{'Recently bought ' + req.recent_purchase + '.' if req.recent_purchase != 'Nothing' else 'No major recent purchase.'} "
                  f"{'Experienced: ' + req.recent_negative_experience + '.' if req.recent_negative_experience != 'None' else ''}",
        "influences": f"Influence score: {req.influence_score}/100. Current need: {req.current_need}."
    }


def explain_decision(req: ChatRequest) -> dict:
    if not FIREWORKS_API_KEY or req.state == "wait":
        return get_local_explanation(req)

    try:
        from openai import OpenAI
        client = OpenAI(base_url=FIREWORKS_BASE_URL, api_key=FIREWORKS_API_KEY)

        prompt = f"""You are an XAI system. Explain why this agent made their decision.

Agent: {req.agent_type}, {req.profession}, {req.location}
Income: ${req.income:,.0f}/yr | Savings: ${req.savings:,.0f} | Monthly expenses: ${req.monthly_expenses:,.0f}
Mood: {req.mood} | Financial status: {req.financial_status}
Product: {req.product} at ${req.price:,.0f}
Decision: {req.state.upper()}
Recent negative experience: {req.recent_negative_experience}
Current need: {req.current_need}

Return ONLY this JSON (no other text):
{{"decision":"Adopted|Rejected|Waiting","probability":"XX%","reason":"2-3 sentence explanation referencing specific financial data","confidence":"High/Medium/Low (XX%)","counterfactual":"What would change their decision","memory":"What past experience influenced this","influences":"Key external factors"}}"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=300,
            temperature=0.2,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[Simulyn] Explainability error: {e}")
        return get_local_explanation(req)

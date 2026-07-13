from .config import FIREWORKS_API_KEY, FIREWORKS_BASE_URL, MODEL_NAME
from .schemas.pydantic_schemas import SummaryRequest

def generate_report(req: SummaryRequest) -> str:
    total = req.total_buyers + req.total_rejectors + req.total_waiting
    adoption_rate = round((req.total_buyers / total) * 100, 1) if total > 0 else 0
    uncertainty_pool = req.total_waiting / total if total > 0 else 0
    confidence_score = min(99, 100 - (uncertainty_pool * 100) / 2)
    variance = req.revenue * uncertainty_pool

    # Generate LLM Insights (Max 250 tokens)
    llm_insights = ""
    if FIREWORKS_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(base_url=FIREWORKS_BASE_URL, api_key=FIREWORKS_API_KEY)
            
            prompt = f"""
You are an Executive Business Intelligence AI.
Given the simulation outcomes, generate a concise Executive Insight paragraph (3-4 sentences).
Focus strictly on the business opportunity, major risks, and one strategic recommendation.
Do NOT use markdown. Do NOT use HTML. Do NOT output lists.

SIMULATION OUTPUTS:
- Product: {req.product} | Price: ${req.price:,.0f}
- Results: {req.total_buyers} buyers ({adoption_rate:.1f}% adoption) | {req.total_rejectors} rejectors | {req.total_waiting} undecided
- Predicted Revenue: ${req.revenue:,.0f} ±${variance:,.0f}
- Confidence: {confidence_score:.1f}%
- Risks identified: {req.risks}
"""
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.3,
            )
            import re
            text = response.choices[0].message.content.strip()
            text = re.sub(r'<think>.*?(?:</think>|$)', '', text, flags=re.IGNORECASE | re.DOTALL).strip()
            llm_insights = f"""
            <div style="background:#1e1b4b;border:1px solid #4338ca;border-radius:12px;padding:20px;margin-bottom:24px;">
                <div style="font-size:10px;color:#a5b4fc;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">AI Executive Insight</div>
                <div style="font-size:14px;color:#e0e7ff;line-height:1.6;font-weight:500;">
                    {text}
                </div>
            </div>
            """
        except Exception as e:
            print(f"[Simulyn] LLM Insight generation error: {e}")

    # Build events summary if available
    events_html = ""
    if req.timeline_events:
        events_list = req.timeline_events[:5]  # top 5
        items = "".join(
            f'<li style="margin-bottom:6px; color:#9ca3af;">{str(ev)[:120]}</li>'
            for ev in events_list
        )
        events_html = f"""
        <div style="background:#0d1020;border:1px solid #1e2332;border-radius:12px;padding:20px;margin-top:8px;">
            <div style="font-size:10px;color:#4b5563;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px;">Simulation Timeline (Facts)</div>
            <ul style="list-style:disc;padding-left:16px;font-size:11px;line-height:1.8;">{items}</ul>
        </div>"""

    return f"""
    <div style="font-family: Inter, sans-serif; color: #e2e8f0; max-width:100%;">
        <div style="border-bottom: 1px solid #1e2332; padding-bottom: 20px; margin-bottom: 24px;">
            <div style="font-size: 11px; color: #4b5563; text-transform: uppercase; letter-spacing: .1em; margin-bottom: 6px;">Simulyn Executive Intelligence</div>
            <h1 style="font-size: 24px; font-weight: 800; color: #fff; margin: 0 0 4px;">{req.product}</h1>
            <p style="font-size: 13px; color: #6b7280; margin: 0;">30-Day Simulation · {total} Agents · {req.target_audience}</p>
        </div>

        {llm_insights}

        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;">
            {"".join(f'''<div style="background:#141820;border:1px solid {bc};border-radius:12px;padding:16px;text-align:center;">
                <div style="font-size:10px;color:#4b5563;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">{label}</div>
                <div style="font-size:24px;font-weight:800;color:{vc};">{val}</div>
            </div>''' for label, val, vc, bc in [
                ("Simulation Conf.", f"{confidence_score:.1f}%", "#6366f1", "#6366f133"),
                ("Buyers", str(req.total_buyers), "#10b981", "#10b98133"),
                ("Rejectors", str(req.total_rejectors), "#ef4444", "#ef444433"),
                ("Adoption Rate", f"{adoption_rate:.1f}%", "#fff", "#1e2332"),
            ])}
        </div>

        <div style="background:#0d1020;border:1px solid #1e2332;border-radius:12px;padding:20px;margin-bottom:20px;">
            <div style="font-size:10px;color:#4b5563;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">Projected Revenue (Prediction)</div>
            <div style="font-size:18px;font-weight:700;color:#fff;">${req.revenue:,.0f} <span style="font-size:14px;color:#4b5563;font-weight:400;">±${variance:,.0f}</span></div>
            <div style="font-size:11px;color:#9ca3af;margin-top:8px;">Based on {req.total_buyers} conversions at ${req.price:,.0f} MSRP. Variance is derived from {req.total_waiting} undecided agents in the network.</div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
            <div style="background:#141820;border:1px solid #1e2332;border-radius:12px;padding:20px;">
                <div style="font-size:10px;color:#818cf8;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px;">Assumptions & Setup</div>
                <ul style="list-style:disc;padding-left:16px;color:#9ca3af;font-size:12px;line-height:2;">
                    <li>Marketing Budget: ${req.marketing_budget:,.0f}</li>
                    <li>Price Point: ${req.price:,.0f}</li>
                    <li>Target Market: {req.target_audience}</li>
                    <li>Competitors: {req.competitors}</li>
                </ul>
            </div>
            <div style="background:#141820;border:1px solid #1e2332;border-radius:12px;padding:20px;">
                <div style="font-size:10px;color:#f59e0b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px;">Identified Risks</div>
                <ul style="list-style:disc;padding-left:16px;color:#9ca3af;font-size:12px;line-height:2;">
                    <li>{req.risks}</li>
                    <li>{req.total_rejectors} agents explicitly rejected the offering.</li>
                    <li>{req.total_waiting} agents remained undecided due to insufficient social pressure.</li>
                </ul>
            </div>
        </div>

        {events_html}

        <div style="margin-top:24px;padding-top:16px;border-top:1px solid #1e2332;font-size:10px;color:#374151;text-align:center;">
            Data derived from PyTorch network simulation · SKPI Intelligence Embedded
        </div>
    </div>
    """

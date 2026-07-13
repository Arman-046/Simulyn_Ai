from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .schemas.pydantic_schemas import ScenarioExtractRequest, BenchmarkRequest, ChatRequest, SummaryRequest, SimulationRequest, PopulationRequest, RunSimulationRequest
from .database import get_db, AsyncSession, async_session

from sqlalchemy import select
from .schemas.models import User, Scenario, Simulation, SimulationResult
import uuid

from .extraction import extract_scenario_data
from .explainability import explain_decision
from .reporting import generate_report
from .simulation import run_benchmark
from .engine import run_pytorch_simulation
from .population import generate_population
import asyncio

try:
    import torch
except ImportError:
    torch = None

app = FastAPI(title="Simulyn Enterprise API", version="3.0", default_response_class=ORJSONResponse)

@app.on_event("startup")
async def startup_event():
    async with async_session() as session:
        stmt = select(User).where(User.email == "system@simulyn.local")
        result = await session.execute(stmt)
        if not result.scalars().first():
            sys_user = User(email="system@simulyn.local", role="system")
            session.add(sys_user)
            await session.commit()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "online", "pytorch_installed": torch is not None}

@app.post("/api/generate_population")
async def api_generate_population(req: PopulationRequest, db: AsyncSession = Depends(get_db)):
    result = await asyncio.to_thread(generate_population, req.scenario, req.num_nodes)
    scenario_id_str = req.scenario.get("id")
    if scenario_id_str:
        sim = Simulation(scenario_id=uuid.UUID(scenario_id_str), status="POPULATED", population_data=result)
        db.add(sim)
        await db.commit()
        await db.refresh(sim)
        result["simulation_id"] = str(sim.id)
    return result

@app.post("/api/extract_scenario")
async def extract_scenario(req: ScenarioExtractRequest, db: AsyncSession = Depends(get_db)):
    result = await asyncio.to_thread(extract_scenario_data, req.text)
    
    stmt = select(User).where(User.email == "system@simulyn.local")
    user_res = await db.execute(stmt)
    sys_user = user_res.scalars().first()
    
    if sys_user:
        product = result.get("product_name", {}).get("value", "Unknown")
        
        # safely get price as float
        price_val = result.get("price", {}).get("value", 0.0)
        try:
            price = float(price_val)
        except (ValueError, TypeError):
            price = 0.0

        scen = Scenario(user_id=sys_user.id, product_name=product, price=price, extracted_params=result)
        db.add(scen)
        await db.commit()
        await db.refresh(scen)
        result["id"] = str(scen.id)
    return result

@app.post("/api/benchmark")
async def benchmark(req: BenchmarkRequest, db: AsyncSession = Depends(get_db)):
    return await asyncio.to_thread(run_benchmark, req)

@app.post("/api/generate_chat")
async def generate_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    return await asyncio.to_thread(explain_decision, req)

@app.post("/api/executive_summary")
async def executive_summary(req: SummaryRequest, db: AsyncSession = Depends(get_db)):
    html = await asyncio.to_thread(generate_report, req)
    return {"report_html": html}

@app.post("/api/simulate")
async def simulate(req: RunSimulationRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Simulation).where(Simulation.id == req.simulation_id)
    sim_res = await db.execute(stmt)
    sim = sim_res.scalars().first()
    
    if not sim or not sim.population_data:
        raise HTTPException(status_code=404, detail="Simulation not found or population data missing.")
        
    scen_stmt = select(Scenario).where(Scenario.id == sim.scenario_id)
    scen_res = await db.execute(scen_stmt)
    scenario = scen_res.scalars().first()
    
    price = scenario.price if scenario else 100.0
    budget = 1000000.0
    appeal_score = 0.5
    if scenario and scenario.extracted_params:
        try:
            budget = float(scenario.extracted_params.get("marketing_budget", {}).get("value", 1000000))
        except:
            pass
        try:
            appeal_score = float(scenario.extracted_params.get("product_appeal_score", {}).get("value", 0.5))
        except:
            pass
            
    engine_req = SimulationRequest(
        price=price,
        marketing_budget=budget,
        product_appeal_score=appeal_score,
        agents=sim.population_data.get("agents", []),
        links=sim.population_data.get("links", [])
    )
    
    result = await asyncio.to_thread(run_pytorch_simulation, engine_req)
    
    sim_result = SimulationResult(
        simulation_id=sim.id,
        history=result.get("history", []),
        reasoning_traces=result.get("reasoning_traces", {})
    )
    db.add(sim_result)
    sim.status = "COMPLETED"
    await db.commit()
    
    return result

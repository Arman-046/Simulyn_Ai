import uuid
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    role: Mapped[str] = mapped_column(String, default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Scenario(Base):
    __tablename__ = "scenarios"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    product_name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    extracted_params: Mapped[dict] = mapped_column(JSON)

class Simulation(Base):
    __tablename__ = "simulations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scenarios.id"))
    status: Mapped[str] = mapped_column(String, default="PENDING")
    job_id: Mapped[str] = mapped_column(String, nullable=True)
    population_data: Mapped[dict] = mapped_column(JSON, nullable=True)

class SimulationResult(Base):
    __tablename__ = "simulation_results"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulations.id"))
    history: Mapped[dict] = mapped_column(JSON)
    reasoning_traces: Mapped[dict] = mapped_column(JSON)

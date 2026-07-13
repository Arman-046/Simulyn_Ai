import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.schemas.models import Base, User, Scenario, Simulation
from backend.database import engine, async_session, get_db

def test_engine_initialization():
    """Verify that the engine and sessionmaker are properly instantiated."""
    assert engine is not None
    assert async_session is not None
    assert engine.url.render_as_string(hide_password=False).startswith("postgresql+asyncpg://")

def test_models_metadata():
    """Verify that the Base metadata contains all expected tables."""
    tables = Base.metadata.tables.keys()
    assert "users" in tables
    assert "scenarios" in tables
    assert "simulations" in tables

@pytest.mark.asyncio
async def test_get_db_generator():
    """Verify that get_db yields an AsyncSession."""
    db_gen = get_db()
    try:
        session = await anext(db_gen)
        assert isinstance(session, AsyncSession)
    except StopAsyncIteration:
        pytest.fail("Generator did not yield a session")
    finally:
        await db_gen.aclose()

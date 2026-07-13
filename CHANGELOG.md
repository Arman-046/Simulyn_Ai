# Changelog

All notable changes to this project will be documented in this file.

## [3.0.0] - 2026-07-12
### Added
- **PKG-004 Option B Persistence**: Completely refactored database to isolate inputs (`simulations`) from outputs (`simulation_results`), eliminating Postgres MVCC transaction deadlocks.
- **ORJSON**: Implemented global `ORJSONResponse` in FastAPI yielding a 7.66x serialization speedup.
- **Pydantic Validation**: Strict `UUID4` validation on `/simulate` endpoint to prevent `500` server errors from malformed client input.
- **Frontend Throttling**: Implemented intelligent array slicing (`limit 500`) to prevent D3.js DOM explosion on large populations, while preserving complete statistical accuracy in Chart.js.

## [2.0.0] - 2026-07-10
### Added
- **PyTorch Engine**: Migrated from native Python math to `torch.sparse.mm` for ultra-fast, GPU-accelerated O(E) Bass Diffusion calculations.
- **Fireworks LLM**: Integrated DeepSeek-v4-Pro for dynamic SKPI (Synthetic Key Performance Indicator) extraction.
- **Docker-Compose**: Standardized local deployments across Postgres 15 and Redis.

## [1.0.0] - 2026-07-01
### Added
- Initial Hackathon proof of concept.
- Basic FastAPI + React/D3 implementation.

# Release Notes

## Version 3.0 (Enterprise Release Candidate)
*Date: 2026-07-12*

Simulyn Version 3.0 finalizes the Enterprise Architecture and prepares the repository for the AMD Hackathon final submission. 

### Key Highlights
- **Unprecedented Performance**: The integration of PyTorch sparse matrix math coupled with `orjson` serialization allows for simulating tens of thousands of market agents in under 100 milliseconds.
- **Bulletproof Persistence**: The migration to 'Option B' persistence prevents Postgres write amplification. Inputs and outputs are strictly isolated.
- **Rock-Solid Security**: API payload vulnerabilities discovered during the QA sprint have been completely neutralized via strict Pydantic type enforcements.

### Hackathon Judging Information
This release candidate is exactly what will be demonstrated. Review the `README.md` and `DEVELOPER_GUIDE.md` for running the application locally.

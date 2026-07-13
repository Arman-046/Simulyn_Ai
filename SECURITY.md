# Security Policy

## Supported Versions

Currently, Simulyn Enterprise is in active development for the AMD Hackathon. Only the latest commit on the `main` branch receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 3.x     | :white_check_mark: |
| < 3.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within Simulyn, please send an email to the repository maintainers rather than opening a public issue.

## Known Security Limitations
- **Authentication**: The FastAPI endpoints currently lack JWT/OAuth authentication. Do not deploy this API to the open web without placing it behind an authenticating API Gateway or implementing a middleware auth layer.
- **Data Pruning**: The `simulation_results` table is append-only. Long-running production instances will require a cron job to prune old tensor outputs to prevent disk exhaustion.

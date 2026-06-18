# Backend Structure

The backend is organized as an Express + TypeScript service.

## Directories

- `src/config`: environment, database, and runtime configuration
- `src/controllers`: HTTP request handlers
- `src/middlewares`: Express middleware
- `src/models`: backend-facing data models and DTOs
- `src/routes`: API route definitions
- `src/services`: business logic
- `src/utils`: shared backend utilities
- `tests`: backend tests

Keep controllers thin. Put business rules in services and data access behind small, testable interfaces.

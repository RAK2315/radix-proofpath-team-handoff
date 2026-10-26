# Shared once, used by all five teammates

- `requirements.lock.txt`, `requirements.runtime.lock.txt`, `pyproject.toml`: pinned Python setup.
- `package.json`, `package-lock.json`: React/Vite/TypeScript, shared UI and test dependencies.
- `shared/contracts/`: canonical Pydantic models, OpenAPI and generated TypeScript. Do not independently rename fields.
- `shared/integrations/`: private documents, records/auth, Groq transport/schema checks, quotas and receipts.
- `shared/ui/`: API helpers, generic controls, context and source drawer.
- `apps/api/main.py`, `apps/web/`: the complete baseline application, composition only.
- `apps/api/standalone.py`, `apps/api/handoff.py`, `apps/module-web/`: isolated feature composition and local synthetic input loader.
- `data/synthetic/` and `demo/final/`: reusable invented assets, benchmarks and validated JSON snapshots.
- `tests/`, `conftest.py`: generic fixtures, integration/browser checks and provider mocks.

The standalone API loads only the selected feature router; it does not forward requests to another module
server. Stored upstream synthetic fixtures supply missing inputs. Module 5 depends on Module 4's pure
readiness scorer and benchmark repository as in the integrated app. Both source folders are in this clone.
The current root app and some existing integration tests import all five baseline modules; keep the full
clone rather than deleting other folders. There is no need to install five virtualenvs or five node_modules.

# Backend contracts and simulated API
Owner: B1 · Branch: `be/contratos-api-simulada` · Status: needs decision · Delivery: sliced commits in one PR

## Specs
1. **S1** — "comienza con el punto 1"
2. **S2** — "ok procede"
3. **S3** — "No se de que me hablas, especificame."
4. **S4** — "si"
5. **S5** — "Objetos con listas"
6. **S6** — "Unión estricta"
7. **S7** — "Inicio y fin obligatorios"

## Tasks
- [x] **T1** · S1-S2, S5-S7 · delegated · commits: `f474e09`, `274c2ce`, `59a3f69` — Complete one TDD work unit covering the Python 3.11 scaffold, contracts, constants, simulated fixtures, and `/api/v1` endpoints.
- [~] **T2** · S1-S2 · merged into T1 · commit: n/a — Contract implementation merged into the active TDD work unit after RED.
- [~] **T3** · S1-S2 · merged into T1 · commit: n/a — Simulated API implementation merged into the active TDD work unit after RED.
- [!] **T4** · S1-S3 · inline · commit: `40ccbd8` — Docker, backend CI, package skeleton and local instructions implemented; functional image build blocked by Docker registry/engine connectivity.
- [x] **T5** · S2-S4 · inline · commits: `f474e09`..`40ccbd8` — Full local checks and blocker-aware owner-review handoff prepared; first offline-demo snapshot before hour 36 remains a follow-up dependency.
- [!] **T6** · S2 · native review · commit: n/a — Native review blocked because managed assets were outdated and the exact provider `sync --agent pi` continuation timed out.

## Log
- **L1** — "comienza con el punto 1"
- **L2** — "ok procede"
- **L3** — "No se de que me hablas, especificame."
- **L4** — "si"
- **L5** — Scope interpretation: execute the B1 backend portion of issue #1 locally first. Public HTTPS deployment remains after local verification and requires a hosting account; frontend implementation remains with F1.
- **L6** — "Objetos con listas"
- **L7** — "Unión estricta"
- **L8** — "Inicio y fin obligatorios"
- **L9** — RED observed with `backend/.venv/Scripts/python.exe -m pytest -q`: 23 failed and 42 errors because `app` does not exist; Ruff lint passed and tests were formatted.
- **L10** — T2 and T3 were merged into T1 so the contract tests and the minimal implementation close one coherent TDD work unit.
- **L11** — First review slice committed as `f474e09` (contracts, constants, focused tests), 643 authored lines. This is the smallest coherent contract slice found and exceeds the approximate 400-line review target.
- **L12** — Delivery strategy selected: multiple behavior-focused commits in one PR.
- **L13** — Initial GREEN: 68 tests passed. Independent verification surfaced simulated-input validation gaps; correction RED was 55 failed / 10 passed, then GREEN reached 133 passed. Ruff check and format pass; wheel inspection includes `app/**` and excludes `verascope_datos`.
- **L14** — API/fixture slice committed as `274c2ce`; validation correction slice committed as `59a3f69`.
- **L15** — T4 structural RED: 8 failed / 1 passed because Dockerfile, .dockerignore, backend CI, jobs package and README instructions were absent. Structural GREEN: 9 passed; full suite 142 passed and Ruff check/format pass.
- **L16** — Local uvicorn smoke passed at `/api/v1/salud` with `simulado=true`. Docker BuildKit ended with `DeadlineExceeded`; the bounded classic-builder attempt reached `FROM python:3.11-slim` and stopped on a Docker Hub TLS handshake timeout. `docker images` then timed out, so functional image proof is inaccessible in this environment.
- **L17** — T4 committed as `40ccbd8`. Local evidence: 142 tests passed, Ruff check/format passed, wheel contents included `app/**` and excluded `verascope_datos`, and uvicorn health smoke passed.
- **L18** — Independent verifier execution was unavailable in its scratch environment, but its four static findings were converted to regression tests and corrected. Native review became due, then stopped on `managed_assets_outdated`; the exact sync continuation timed out after 30 seconds and was not retried.
- **L19** — The user requested a backend-role branch instead of working on the main/shared branch. Existing B1 commits were preserved on `be/contratos-api-simulada`; `main` remains untouched.

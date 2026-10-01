# TransGIS verification

## Default: deterministic and offline

From `backend/`:

```bash
python -m pytest -m "not live" -v
```

The default `python -m pytest` also skips live tests unless explicitly enabled.
No credentials, database, public provider availability, or model subscription are required.
The autouse fixture blocks real HTTPX transports, PostgreSQL connections and
socket.create_connection. It fails at teardown if application code swallowed a blocked
attempt. In-process ASGITransport and HTTPX MockTransport remain usable.

The suite covers geometry and spatial resolution, metric validation, fixture-backed
FDOT/Socrata requests, tool validation and dispatch, deterministic agent answers,
location lookup normalization, and API validation. Operational and security tests
exercise their own local state. Fixtures are synthetic examples of provider schemas;
passing these tests does not establish current public service availability or universal
geographic coverage.

Agent behavior tests assert source values and provenance, no hourly substitution from
AADT, ambiguity handling, and refusal to infer live congestion from annual averages.
They intentionally avoid assertions tied to a particular model's wording.

## Opt-in: live public provider contracts

PowerShell:

```powershell
$env:TRANSGIS_RUN_LIVE_TESTS = "1"
python -m pytest tests/live -m live -v
Remove-Item Env:TRANSGIS_RUN_LIVE_TESTS
```

POSIX:

```bash
TRANSGIS_RUN_LIVE_TESTS=1 python -m pytest tests/live -m live -v
```

These checks request FDOT layer metadata, one Gainesville site, and one Photon search
result. They do not call NaviGator or write to a production database. Timeouts, rate
limits, retired datasets, and field changes are real failures requiring investigation,
rather than fabricated empty results. Run them when reviewing provider changes and
before releases. A failed public service check should not be confused with a regression
in deterministic application behavior.

## CI separation

Push and pull-request CI runs the offline backend suite and the frontend production
build. Public provider checks run only from the workflow's manual dispatch with
`live_providers` selected. Each backend job uploads JUnit results independently.
No provider credentials are supplied to the normal CI job.

## Frontend

From `frontend/`:

```bash
npm ci
npm run build
```

The build checks TypeScript and bundling. It is not a browser usability test. Verify
map selection, source coverage labels, dropdown keyboard controls, responsive layout,
and analysis-job progress separately in a browser.

## Evidence discipline

Record actual command output and environment when reporting a verification result.
Do not retain an unconditional "all passed" table after changing code. Production
readiness additionally needs an actual deployed database/cache, identity configuration,
load testing, and the live provider checks; mocked tests cannot prove those properties.

# Ghost Lantern Labs – Cloud Readiness (Azure Focus)

## 1. Overview

Ghost Lantern Labs (GLL) is being designed as a modular fusion engine:

- Ingests multi-domain telemetry (seismic, radiation, comms)
- Applies validation + physics-aware checks
- Scores events and produces commander-ready extracts
- Generates alerts and daily summary reports

This document tracks how the current local pipeline will map to Azure services.

---

## 2. Current Local Pipeline (v0.1)

Local core modules in `src/`:

- `build_fused_output.py`  → generates/assembles fused_output.csv
- `fusion_scoring.py`      → reads fused_output.csv, writes scored_output.csv
- `commander_extract.py`   → builds commander_extract.csv from scored_output.csv
- `heatmap_prep.py`        → builds heatmap_data.csv
- `fusion_alerts.py`       → detects critical events, writes critical_alerts.csv
- `daily_report.py`        → produces daily_report.txt
- `fusion_logger.py`       → writes fusion_ops_log.csv
- `validators.py`          → schema, physics, and integrity validators
- `schema_loader.py`       → loads baseline_schema.csv
- `settings.py`            → central paths/params (local)

All of this currently runs on a single machine via `poetry run python ...`.

---

## 3. Target Azure Mapping (Concept Draft)

### 3.1 Storage

**Local:**
- `fused_output.csv`
- `scored_output.csv`
- `commander_extract.csv`
- `heatmap_data.csv`
- `critical_alerts.csv`
- `fusion_ops_log.csv`
- `daily_report.txt`

**Azure Target:**
- Azure Blob Storage container, e.g. `gll-data`:
  - `raw/`                → original sensor logs
  - `fused/`              → fused_output equivalents
  - `scored/`             → scored_output equivalents
  - `commander/`          → commander_extract equivalents
  - `heatmap/`            → heatmap-ready data
  - `alerts/`             → critical_alerts
  - `logs/`               → fusion_ops_log style data
  - `reports/`            → daily_report-style outputs

Baseline schema (`baseline_schema.csv`) will eventually live as a managed config
(e.g., in Blob, Table Storage, or Key Vault / App Config) instead of just on disk.

---

### 3.2 Compute (Azure Functions – Future Targets)

Candidate Azure Functions (one function per logical module):

1. `gll-fusion-scoring-fn`
   - Trigger: Blob upload in `fused/`
   - Action: Run scoring logic (current `fusion_scoring.py`)
   - Output: Write `scored/` blob

2. `gll-commander-extract-fn`
   - Trigger: Blob upload in `scored/`
   - Action: Build commander extract (current `commander_extract.py`)
   - Output: Write `commander/` blob

3. `gll-heatmap-prep-fn`
   - Trigger: Blob upload in `scored/`
   - Action: Build heatmap-ready telemetry
   - Output: Write `heatmap/` blob

4. `gll-alerts-fn`
   - Trigger: Blob upload in `commander/` OR `scored/`
   - Action: Check for critical events, emit alerts
   - Output: Write `alerts/` blob + log events

5. `gll-daily-report-fn`
   - Trigger: Timer (e.g. once per day)
   - Action: Summarize last 24h (scored + alerts)
   - Output: `reports/` + log events

All functions will call a shared validator library (today: `validators.py` + `schema_loader.py`)
and a shared logging library (today: `fusion_logger.py`).

---

### 3.3 Monitoring / Logging

**Local:**
- `fusion_ops_log.csv` log file
- Print statements

**Azure Target:**
- Azure Application Insights / Azure Monitor for:
  - Function logs
  - Custom events (equivalent to `fusion_ops_log`)
  - Basic metrics (pipeline success/failure, alert counts)

Long-term goal: send validation failures and physics anomalies as structured telemetry to a log analytics workspace.

---

## 4. Cloud Readiness Status (v0.1)

### ✅ Already in place (local):

- Modular pipeline: each step is a separate Python module
- Central logging via `fusion_logger.log_event`
- Physics-aware validation with `validators.py`
- Schema-driven validation via `baseline_schema.csv` + `schema_loader.py`
- End-to-end pipeline proven locally using Poetry

### 🔧 Needed before first Azure deployment:

1. Centralize configuration in `settings.py` so paths become environment-driven.
2. Abstract file I/O (read/write CSV) so it can target:
   - Local filesystem OR
   - Azure Blob (using a small storage adapter)
3. Wrap each step in a function signature friendly to Azure Functions (e.g., `(blob: InputStream) -> OutputBlob`).
4. Decide on minimal error-handling strategy for cloud failures (currently `safe_run` + logging).

---

## 5. First Azure Milestone Plan (High Level)

**Milestone 1 — “Cloud-Sim Ready” (Pre-BMT)**

- Document mappings (this file)
- Keep code modular and validator-driven
- Ensure `settings.py` cleanly abstracts local paths

**Milestone 2 — “Azure Emulation” (Post-BMT / during Tech School)**

- Write small storage abstraction (local vs cloud)
- Simulate Azure-style flows on local using function wrappers

**Milestone 3 — “Real Azure Test Deployment”**

- Deploy one function (e.g., scoring) to Azure Functions
- Wire to Blob container
- Verify end-to-end: Blob in → Scored Blob out → Logs in Monitor

---

## 6. Notes for Future Implementation

- Azure will be the **primary cloud** for GLL moving forward.
- Fusion validation + schema enforcement must never be bypassed in the cloud version.
- All operational runs (cloud or local) should log via a consistent event schema
  (module, status, note, timestamp) for future analytics and dashboards.

This document will evolve as GLL matures and as Azure is brought online in phases.


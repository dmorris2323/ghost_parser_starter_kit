# Ghost Lantern Labs — Azure Edge Architecture (v1 Stub)

**Goal:** Define how `fused_output.csv` will flow from edge collection to Azure, 
without actually calling Azure yet.

## 1. Edge / Local Pipeline (Today)

1. Seismic events captured or simulated into `data/seismic_events.csv`
2. `build_fused_output_from_seismic.py` converts this into:

   `data/fused_output.csv`

   with schema:

   - id
   - Seismic_Mag
   - Radiation_uSv
   - Comms_State
   - AOI_Hit

3. `fusion_scoring.py` reads `data/fused_output.csv`, validates schema, 
   applies physics-aware checks, and writes `scored_output.csv`.

4. `commander_extract.py` builds `commander_extract.csv` (top events).

5. `heatmap_prep.py` builds `heatmap_data.csv` for visualization.

6. `fusion_alerts.py` generates `critical_alerts.csv` when needed.

7. `daily_report.py` builds `daily_report.txt`.

8. `qa_validator.py` runs the full pipeline as a one-button QA harness.

## 2. Azure v1 (Design Only — No Real Upload Yet)

Planned flow:

1. Edge system (laptop / field server) runs full GLL pipeline.
2. Verified `data/fused_output.csv` is treated as the "truth" telemetry feed.
3. A small uploader script (azure_upload_stub.py) checks for the file and
   prints what it WOULD send to Azure Blob Storage.

Planned future behavior (v2+):

- Upload target: Azure Blob container named `gll-telemetry`
- Blob path pattern: `edge_runs/{YYYYMMDD}/{HHMMSS}/fused_output.csv`
- Azure Function (future) triggers on new blob, runs scoring/alert logic in the cloud.
- Alerts/summary pushed into a secure web dashboard for commanders.

## 3. Why This Matters

- Keeps GLL **edge-first**: pipeline works with or without cloud.
- Creates a clean seam between **edge pipeline** and **cloud pipeline**.
- Gives a clear hand-off point for future Azure engineering work.
- Matches DoD reality: intermittent connectivity, local-first processing,
  and cloud as an amplifier, not a crutch.

## 4. Current Implementation Status (Day 48)

- Edge pipeline: WORKING
- Schema validation: WORKING (baseline_schema.csv + validators)
- QA harness: WORKING (qa_validator.py)
- Azure integration: STUB ONLY (azure_upload_stub.py)

---

## Day 50 – Component & File Map

### 1. Core Azure Components (Planned)

1. **Blob Storage**
   - Container name (planned): `gll-telemetry`
   - Purpose: store raw and processed fusion files from the edge.
2. **Azure Functions (Python)**
   - Triggers on new blobs in `gll-telemetry`.
   - Tasks:
     - Validate schema.
     - Re-score or verify events.
     - Raise cloud-side alerts.
3. **Table Storage / Cosmos DB (TBD)**
   - Long-term storage for:
     - Alert history
     - Commander extracts
     - Ops logs and QA results
4. **Web Dashboard / Command Console**
   - Reads from Blob + Table/Cosmos.
   - Displays heatmaps, timelines, and alert status.

---

### 2. Edge → Cloud File Flow (Day 50)

**Source system:** Ghost Lantern Labs edge pipeline (your laptop)

Files produced locally:

- `data/fused_output.csv` → fused telemetry
- `src/scored_output.csv` → scored events
- `src/commander_extract.csv` → commander summary
- `src/critical_alerts.csv` → filtered critical events
- `src/daily_report.txt` → daily human-readable report

**Planned upload targets:**

- Blob container `gll-telemetry`:
  - Raw fusion: `fused_output.csv`
  - Scored fusion: `scored_output.csv`
  - Alerts: `critical_alerts.csv`
  - Command summaries: `commander_extract.csv`
- Optional: a separate container or path for `daily_report.txt`.

---

### 3. Edge Client — Azure Stub

Day 50 adds:

- `src/cloud/azure_client_stub.py`

Responsibilities:

- Check that a given fusion file exists.
- Log/print that it is “ready for upload”.
- Act as the drop-in location where Azure SDK calls will be added later.

This keeps GLL:

- Fully operational **offline**, and
- Ready for **instant cloud integration** when we flip the switch.


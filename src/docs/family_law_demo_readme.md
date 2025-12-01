# Ghost Lantern Labs — Family Law Demo (Shari)

## Purpose

This demo shows how GLL can help a family law or collections attorney:

- See which cases are most urgent.
- Prioritize work based on risk, deadlines, and client factors.
- Turn raw CSVs into an intel-style brief.

It is designed for:
- Shari (initial hands-on operator).
- Future conference demos (AfroTech, legal tech, small military/legal events).

---

## Data Flow

1. **Input CSV**

   `data/family_law_cases_sample.csv`

   Columns:
   - `case_id`
   - `client_name`
   - `case_type` (custody, support, visitation, etc.)
   - `days_until_hearing`
   - `domestic_violence_flag` (0/1)
   - `prior_contempts`
   - `child_risk_score` (0.0–1.0)
   - `payment_status` (behind / on_time / partial)

2. **Normalization**

   `legal_ingest_family_law.py` → `data/family_law_fused.csv`

   - Cleans types.
   - Converts flags to ints.
   - Adds `payment_behind` flag.

3. **Scoring**

   `family_law_scoring.py` → `data/family_law_scored.csv`

   Score = Weighted mix of:
   - Hearing proximity
   - Child risk
   - DV history
   - Prior contempt
   - Payment behavior

   Outputs:
   - `gll_score` (0–1)
   - `gll_severity` (HIGH / MODERATE / LOW)

4. **Briefing**

   `family_law_brief.py` → `family_law_brief.txt`

   - Sorts cases by score.
   - Lists top 3 urgent cases.
   - Produces a one-page brief.

---

## Demo Flow (for Shari)

From `src` directory:

```bash
python ghost_cli.py
# choose option 15: "Run Family Law Demo (Shari)"


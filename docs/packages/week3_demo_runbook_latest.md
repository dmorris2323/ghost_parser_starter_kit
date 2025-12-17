# Week-3 Demo Runbook — Obasi / GLL (Customer Handoff)

- generated_at_utc: `2025-12-17T19:56:18.999674+00:00`
- context: `week3_demo_runbook_auto_from_packager`

## 0) Demo safety (read this first)
✅ **DEMO MODE ACTIVE (READ ONLY)**

```
DEMO MODE ACTIVE — READ ONLY
No baselines updated. No training. No mutation.
Assessment is probabilistic and bounded; operator judgment applies.
```

## 1) What you should expect (success criteria)
- Orchestrator verdict (latest): **PASS**
- Readiness gate verdict (latest): **PASS**
- Package manifest verdict (latest): **PASS**

## 2) Quickstart (local machine)
From repo root:

```bash
python src/week3_demo_orchestrator.py
```

Then open these files (they are demo-friendly):

```bash
cat docs/briefs/week3_demo_narrative_latest.txt
cat docs/briefs/commander_brief_latest.txt | head -n 80
cat docs/briefs/legal_case_snapshot_latest.txt
cat docs/briefs/week3_operator_summary_latest.txt
cat docs/validation/week3_demo_readiness_gate_latest.txt
```

## 3) If you only have the ZIP (no repo access)
You can still review everything **without running any code**:

1) Unzip the package
```bash
unzip week3_cloud_demo_package_latest.zip -d week3_demo_pkg
cd week3_demo_pkg
```

2) Read the core outputs
```bash
cat docs/briefs/week3_demo_narrative_latest.txt
cat docs/briefs/commander_brief_latest.txt | head -n 80
cat docs/briefs/legal_case_snapshot_latest.txt
cat docs/briefs/week3_operator_summary_latest.txt
cat docs/validation/week3_demo_readiness_gate_latest.txt
cat docs/packages/week3_customer_handoff_one_pager_latest.txt
```

## 4) The “demo script” (what to say while scrolling)
Use this order to control narrative and avoid scope creep:

1) **Narrative**: “This is a read-only demo pack. No baselines updated. No training. No mutation.”
2) **Commander brief**: bounded sections; no attribution claims from synthetic telemetry.
3) **Legal snapshot (Shari Hook)**: fast, familiar hook; shows the same safety philosophy.
4) **Operator summary**: 10-second PASS signal.
5) **Readiness gate**: we refuse to demo if required demo-lock markers are missing.

## 5) Troubleshooting (common issues)
- If a script hangs: it’s usually waiting on a subprocess. Re-run the failing script directly.
- If a gate fails: read `docs/validation/*latest.txt` and fix the named violation first.
- If demo-lock is missing: re-run the artifact generator (e.g., `python src/legal_case_snapshot.py`).

## 6) Non-negotiables (contractor-safe language)
- Outputs are **probabilistic and bounded**.
- Demo data is synthetic/training.
- Operator judgment applies before escalation.

"""
command_grade_brief_export.py

Command-Grade PDF Brief Export (SAFE)
- Builds a commander-friendly brief from the latest:
  - Training curve (AGI / slope / volatility)
  - Fusion validation report (baseline vs injected delta)
  - Latest training feedback recommendation (if present)
  - Latest SIS/SPS gate results (PRE/POST) if present
- Writes:
  - docs/briefs/command_grade_brief_latest.pdf (preferred)
  - docs/briefs/command_grade_brief_latest.txt (always)
  - docs/briefs/command_grade_brief_latest.json (always)

Notes:
- Will attempt PDF generation using reportlab. If reportlab isn't installed, it still writes TXT/JSON.
- This is synthetic/training focused. No real-world sensitive telemetry.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass
class SourcePaths:
    root: Path
    docs_dir: Path
    src_docs_dir: Path


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _read_text(path: Path) -> Optional[str]:
    try:
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _find_repo_root() -> Path:
    # file is src/command_grade_brief_export.py -> repo_root = parents[1]
    return Path(__file__).resolve().parents[1]


def _resolve_sources() -> SourcePaths:
    root = _find_repo_root()
    return SourcePaths(
        root=root,
        docs_dir=root / "docs",
        src_docs_dir=root / "src" / "docs",
    )


def _pick_existing(primary: Path, secondary: Path) -> Path:
    return primary if primary.exists() else secondary


def _load_latest_training_curve(srcs: SourcePaths) -> Tuple[Optional[Dict[str, Any]], str]:
    # prefer src/docs, fallback docs
    p1 = srcs.src_docs_dir / "training" / "training_curve_latest.json"
    p2 = srcs.docs_dir / "training" / "training_curve_latest.json"
    path = _pick_existing(p1, p2)
    data = _read_json(path)
    return data, str(path)


def _load_latest_validation_report(srcs: SourcePaths) -> Tuple[Optional[Dict[str, Any]], str]:
    p1 = srcs.src_docs_dir / "validation" / "fusion_validation_report.json"
    p2 = srcs.docs_dir / "validation" / "fusion_validation_report.json"
    path = _pick_existing(p1, p2)
    data = _read_json(path)
    return data, str(path)


def _load_latest_training_feedback(srcs: SourcePaths) -> Tuple[Optional[Dict[str, Any]], str]:
    p1 = srcs.src_docs_dir / "training" / "training_feedback_latest.json"
    p2 = srcs.docs_dir / "training" / "training_feedback_latest.json"
    path = _pick_existing(p1, p2)
    data = _read_json(path)
    return data, str(path)


def _find_latest_integrity_gate_file(srcs: SourcePaths) -> Optional[Path]:
    # Gate writer sometimes uses docs/integrity/*, sometimes src/docs/integrity/*
    cand_dirs = [
        srcs.src_docs_dir / "integrity",
        srcs.docs_dir / "integrity",
    ]
    latest: Optional[Path] = None
    for d in cand_dirs:
        if not d.exists():
            continue
        for f in d.glob("run_gate_*_*.txt"):
            if latest is None or f.stat().st_mtime > latest.stat().st_mtime:
                latest = f
    return latest


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _brief_payload(
    *,
    training_curve: Optional[Dict[str, Any]],
    training_curve_path: str,
    validation_report: Optional[Dict[str, Any]],
    validation_report_path: str,
    training_feedback: Optional[Dict[str, Any]],
    training_feedback_path: str,
    latest_gate_txt_path: Optional[str],
    latest_gate_txt: Optional[str],
) -> Dict[str, Any]:
    # Extract a few key items safely
    curve = training_curve or {}
    agi = _coerce_float(curve.get("AGI", 0.0), 0.0)
    slope = _coerce_float(curve.get("improvement_slope", 0.0), 0.0)
    vol = _coerce_float(curve.get("volatility_index", 0.0), 0.0)
    dwa = _coerce_float(curve.get("difficulty_weighted_average", 0.0), 0.0)

    v = validation_report or {}
    verdict = (v.get("verdict") or {}).get("status") if isinstance(v.get("verdict"), dict) else v.get("verdict")
    verdict = str(verdict) if verdict is not None else "UNKNOWN"

    delta = v.get("delta_vs_baseline") if isinstance(v.get("delta_vs_baseline"), dict) else {}
    trust_delta = _coerce_float(delta.get("trust_proxy_delta", 0.0), 0.0) if isinstance(delta, dict) else 0.0
    risk_delta = _coerce_float(delta.get("risk_score_delta", 0.0), 0.0) if isinstance(delta, dict) else 0.0

    inputs = v.get("inputs") if isinstance(v.get("inputs"), dict) else {}
    difficulty = str(inputs.get("difficulty", "UNKNOWN")) if isinstance(inputs, dict) else "UNKNOWN"
    pattern_id = str(inputs.get("pattern_id", "NONE")) if isinstance(inputs, dict) else "NONE"

    payload = {
        "generated_at": _utc_now_iso(),
        "safe_notice": "This brief is generated from synthetic/training artifacts and is safe for demos.",
        "sources": {
            "training_curve": training_curve_path,
            "validation_report": validation_report_path,
            "training_feedback": training_feedback_path,
            "latest_gate_txt": latest_gate_txt_path or "NOT_FOUND",
        },
        "headline_metrics": {
            "training": {
                "AGI": round(agi, 2),
                "improvement_slope": round(slope, 3),
                "volatility_index": round(vol, 3),
                "difficulty_weighted_average": round(dwa, 2),
            },
            "validation": {
                "verdict": verdict,
                "difficulty": difficulty,
                "pattern_id": pattern_id,
                "trust_proxy_delta": round(trust_delta, 2),
                "risk_score_delta": round(risk_delta, 2),
            },
        },
        "training_feedback": training_feedback or {"status": "MISSING"},
        "gate_excerpt": (latest_gate_txt[:1200] + "...") if isinstance(latest_gate_txt, str) and len(latest_gate_txt) > 1200 else (latest_gate_txt or "MISSING"),
        "raw": {
            "training_curve": training_curve or {},
            "validation_report": validation_report or {},
        },
    }
    return payload


def _render_txt(brief: Dict[str, Any]) -> str:
    hm = brief.get("headline_metrics", {})
    t = hm.get("training", {}) if isinstance(hm, dict) else {}
    v = hm.get("validation", {}) if isinstance(hm, dict) else {}

    lines = []
    lines.append("GLL COMMAND-GRADE BRIEF (TRAINING + VALIDATION)")
    lines.append(f"Generated: {brief.get('generated_at', 'UNKNOWN')}")
    lines.append("")
    lines.append("SAFE NOTICE:")
    lines.append(str(brief.get("safe_notice", "")))
    lines.append("")
    lines.append("HEADLINE METRICS:")
    lines.append(f"- AGI: {t.get('AGI', 0)}")
    lines.append(f"- Improvement slope: {t.get('improvement_slope', 0)}")
    lines.append(f"- Volatility index: {t.get('volatility_index', 0)}")
    lines.append(f"- Difficulty-weighted avg: {t.get('difficulty_weighted_average', 0)}")
    lines.append("")
    lines.append("VALIDATION:")
    lines.append(f"- Verdict: {v.get('verdict', 'UNKNOWN')}")
    lines.append(f"- Difficulty: {v.get('difficulty', 'UNKNOWN')}")
    lines.append(f"- Pattern: {v.get('pattern_id', 'NONE')}")
    lines.append(f"- Trust delta vs baseline: {v.get('trust_proxy_delta', 0)}")
    lines.append(f"- Risk delta vs baseline: {v.get('risk_score_delta', 0)}")
    lines.append("")
    lines.append("NEXT TRAINING RECOMMENDATION (Recorded, not enforced):")
    tf = brief.get("training_feedback", {})
    try:
        lines.append(json.dumps(tf, indent=2))
    except Exception:
        lines.append(str(tf))
    lines.append("")
    lines.append("LATEST SIS/SPS GATE EXCERPT:")
    lines.append(str(brief.get("gate_excerpt", "MISSING")))
    lines.append("")
    lines.append("SOURCES:")
    for k, p in (brief.get("sources", {}) or {}).items():
        lines.append(f"- {k}: {p}")
    return "\n".join(lines)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _write_pdf_if_possible(pdf_path: Path, brief: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Attempt PDF generation using reportlab.
    Returns: (success, message)
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        _safe_mkdir(pdf_path.parent)

        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter

        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "GLL Command-Grade Brief (Training + Validation)")
        y -= 20

        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Generated: {brief.get('generated_at', 'UNKNOWN')}")
        y -= 20

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Headline Metrics")
        y -= 15

        hm = brief.get("headline_metrics", {})
        t = hm.get("training", {}) if isinstance(hm, dict) else {}
        v = hm.get("validation", {}) if isinstance(hm, dict) else {}

        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"AGI: {t.get('AGI', 0)} | Slope: {t.get('improvement_slope', 0)} | Volatility: {t.get('volatility_index', 0)} | DWA: {t.get('difficulty_weighted_average', 0)}")
        y -= 15
        c.drawString(60, y, f"Validation Verdict: {v.get('verdict', 'UNKNOWN')} | Difficulty: {v.get('difficulty', 'UNKNOWN')} | Pattern: {v.get('pattern_id', 'NONE')}")
        y -= 15
        c.drawString(60, y, f"Delta vs Baseline -> Trust: {v.get('trust_proxy_delta', 0)} | Risk: {v.get('risk_score_delta', 0)}")
        y -= 25

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Next Training Recommendation (Recorded)")
        y -= 15

        c.setFont("Helvetica", 9)
        tf = brief.get("training_feedback", {})
        tf_text = ""
        try:
            tf_text = json.dumps(tf, indent=2)
        except Exception:
            tf_text = str(tf)

        for line in tf_text.splitlines():
            if y < 70:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 9)
            c.drawString(60, y, line[:110])
            y -= 12

        y -= 10
        c.setFont("Helvetica-Bold", 11)
        if y < 90:
            c.showPage()
            y = height - 50
        c.drawString(50, y, "Latest SIS/SPS Gate Excerpt")
        y -= 15

        c.setFont("Helvetica", 8)
        gate = brief.get("gate_excerpt", "MISSING")
        for line in str(gate).splitlines():
            if y < 70:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 8)
            c.drawString(60, y, line[:130])
            y -= 10

        c.save()
        return True, "PDF written via reportlab"
    except Exception as e:
        return False, f"PDF generation skipped/failed: {e.__class__.__name__}: {e}"


def export_command_grade_brief() -> Dict[str, Any]:
    srcs = _resolve_sources()

    training_curve, training_curve_path = _load_latest_training_curve(srcs)
    validation_report, validation_report_path = _load_latest_validation_report(srcs)
    training_feedback, training_feedback_path = _load_latest_training_feedback(srcs)

    latest_gate = _find_latest_integrity_gate_file(srcs)
    latest_gate_txt = _read_text(latest_gate) if latest_gate else None

    brief = _brief_payload(
        training_curve=training_curve,
        training_curve_path=training_curve_path,
        validation_report=validation_report,
        validation_report_path=validation_report_path,
        training_feedback=training_feedback,
        training_feedback_path=training_feedback_path,
        latest_gate_txt_path=str(latest_gate) if latest_gate else None,
        latest_gate_txt=latest_gate_txt,
    )

    # outputs
    out_dir = srcs.docs_dir / "briefs"
    pdf_path = out_dir / "command_grade_brief_latest.pdf"
    txt_path = out_dir / "command_grade_brief_latest.txt"
    json_path = out_dir / "command_grade_brief_latest.json"

    _write_json(json_path, brief)
    _write_txt(txt_path, _render_txt(brief))
    pdf_ok, pdf_msg = _write_pdf_if_possible(pdf_path, brief)

    return {
        "status": "OK",
        "generated_at": brief.get("generated_at"),
        "paths": {
            "pdf": str(pdf_path),
            "txt": str(txt_path),
            "json": str(json_path),
        },
        "pdf": {"success": pdf_ok, "message": pdf_msg},
    }


def main() -> int:
    result = export_command_grade_brief()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


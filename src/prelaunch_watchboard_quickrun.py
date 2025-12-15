from __future__ import annotations

import json

from prelaunch_watchboard import build_prelaunch_watchboard, write_prelaunch_watchboard
from prebrief_trust_annotations import build_prebrief_trust_annotations, write_prebrief_trust_annotations

if __name__ == "__main__":
    wb = build_prelaunch_watchboard(
        trust_score=82,
        risk_score=48,
        alerts={"crit": 0, "high": 3, "anomaly": 14},
        degraded=True,
        comms_state=None,
        radiation_usv=None,
        seismic_mag=None,
        ems_state="NOISY",
        previous_posture="DUTY_OFFICER_NOTIFY",
    )
    paths_wb = write_prelaunch_watchboard(wb)

    ann = build_prebrief_trust_annotations()
    paths_ann = write_prebrief_trust_annotations(ann)

    print("Watchboard paths:")
    print(json.dumps(paths_wb, indent=2))
    print("\nPrebrief annotation paths:")
    print(json.dumps(paths_ann, indent=2))


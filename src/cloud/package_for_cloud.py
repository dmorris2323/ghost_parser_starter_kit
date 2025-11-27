"""
package_for_cloud.py — Day 53
Builds a simple zip payload with key GLL outputs.

This simulates "ready-to-upload" artifacts for Azure or other clouds.
"""

from pathlib import Path
import zipfile

from fusion_logger import log_event

FILES_TO_INCLUDE = [
    Path("scored_output.csv"),
    Path("commander_extract.csv"),
    Path("heatmap_data.csv"),
    Path("daily_report.txt"),
    Path("operator_snapshot.txt"),
]

OUT_ZIP = Path("cloud_payload.zip")


def build_cloud_package() -> None:
    existing_files = [p for p in FILES_TO_INCLUDE if p.exists()]

    if not existing_files:
        msg = "No output files found to package. Run pipeline first."
        print(msg)
        log_event("cloud_package", "no_files", msg)
        return

    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in existing_files:
            zf.write(p, arcname=p.name)

    msg = f"Cloud payload written to {OUT_ZIP} ({len(existing_files)} files included)."
    print(msg)
    log_event("cloud_package", "completed", msg)


if __name__ == "__main__":
    build_cloud_package()


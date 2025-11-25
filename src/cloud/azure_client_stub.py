"""
Day 50: Azure client stub for Ghost Lantern Labs.

This does NOT connect to Azure yet.

Purpose:
- Provide a single place where all future Azure uploads will go.
- Keep the rest of the pipeline cloud-agnostic and offline-first.
"""

from pathlib import Path


class AzureClientStub:
    """
    Lightweight stand-in for a real Azure client.

    In the future, this class will:
      - Authenticate to Azure
      - Upload fusion files (fused_output, scored_output, alerts, etc.)
      - Handle retries, logging, and error reporting

    Today it only:
      - Verifies that the file exists
      - Prints what it *would* upload
    """

    def __init__(self, container_name: str = "gll-telemetry"):
        self.container_name = container_name

    def upload(self, file_path: Path) -> bool:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} not found. Run the fusion pipeline first.")

        size_kb = file_path.stat().st_size / 1024
        print(
            f"[STUB] Would upload '{file_path.name}' "
            f"({size_kb:.1f} KB) to Azure Blob container '{self.container_name}'."
        )
        # In future: return True on success, False on failure after a real attempt.
        return True


def demo():
    """
    Demo function for manual testing.

    Tries to upload the main fused_output.csv from the repo-level data folder:
      data/fused_output.csv
    """

    # Default location based on current Day 48/50 pipeline
    default_fused = Path("data") / "fused_output.csv"

    client = AzureClientStub()
    client.upload(default_fused)


if __name__ == "__main__":
    demo()


# Azure Function Flow (Day 51 Draft)

1. `fused_output.csv` created on edge.
2. Blob Upload → `gll-telemetry` container.
3. Azure Function trigger watches blob.
4. Function runs:
   - scoring
   - alert tagging
   - health checks
5. Writes alerts to `gll-alerts` container.
6. Dashboard reads alerts (future).


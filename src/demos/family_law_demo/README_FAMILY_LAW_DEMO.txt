Ghost Lantern Labs — Family Law Demo (Shari)
=================================================

This folder contains a miniature demo of how GLL can help a family law
or collections attorney prioritize cases and see where the real risk and
urgency live.

Key files:
  - family_law_cases_sample.csv
      Raw input cases (custody, support, visitation).

  - family_law_fused.csv
      Normalized version of the above, cleaned and ready for scoring.

  - family_law_scored.csv
      Same cases with GLL risk/urgency score and severity labels.

  - family_law_brief.txt
      Human-readable prioritization brief, written like an intel summary.

  - threat_memory_stats.txt (optional)
      Counts of past threat/alert memory by severity and profile.

  - alerts_trend.png (optional)
      Simple visual of alert growth over time.

Usage for demo:
  1) Explain that GLL can ingest real case data (CSV) from the firm.
  2) Show how cases become normalized (family_law_fused.csv).
  3) Show how cases are scored and labeled (family_law_scored.csv).
  4) Open family_law_brief.txt and walk through the "Top urgent cases".
  5) If available, show threat_memory_stats.txt and alerts_trend.png
     as examples of how GLL tracks patterns over time.

This is a first proof-of-concept slice of how GLL can become a
case-prioritization and risk-intel engine for law firms.

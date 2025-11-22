# Ghost Lantern Labs – Fused Output Schema (v1)

Purpose: `fused_output.csv` is the single truth table that joins all sensor feeds for scoring, alerting, and reporting.

## Columns

- Event_ID                (string) – unique ID per event
- Event_Time_UTC         (datetime, ISO 8601)
- Sensor_ID              (string)
- Sensor_Type            (string: SEISMIC, RF, POWER, NETWORK, OTHER)
- Geo_Lat                (float, degrees)
- Geo_Lon                (float, degrees)

- Seismic_Mag            (float, 0 if not applicable)
- Radiation_uSv          (float, 0 if not applicable)
- Comms_State            (string: UP, DOWN, DEGRADED, UNKNOWN)
- Power_State            (string: NOMINAL, ABNORMAL, UNKNOWN)
- Network_Anomaly_Score  (float, 0–100, 0 if not applicable)

- Threat_Score           (float, 0–100)
- Alert_Level            (string: GREEN, AMBER, RED)

## Mandatory for scoring (v1)

- Seismic_Mag
- Radiation_uSv
- Comms_State
- Threat_Score

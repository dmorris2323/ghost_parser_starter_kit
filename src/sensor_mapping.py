"""
sensor_mapping.py — Ghost Lantern Labs
--------------------------------------

Defines which normalized numeric fields we pull from each sensor type.

This provides consistency across ALL sensors so that the fusion layer
does not need to know which sensor produced which fields.
"""

SENSOR_FIELD_MAP = {

    "optical": {
        "intensity": "intensity_norm",
        "cloud_score": "cloud_score",
        "flash_flag": "flash",
    },

    "seismic": {
        "mag": "mag",
        "distance": "distance_km",
        "snr": "snr_db",
        "yield_proxy": "threat_score",
    },

    "ems": {
        "jamming_flag": "jamming",
        "snr": "snr_db",
        "anomaly": "anomaly_score",
        "ems_threat": "ems_threat",
    },

    "radiation": {
        "background": "background_uSv",
        "current": "current_uSv",
        "delta": "delta_uSv",
        "spike_flag": "spike",
    },

    "generic": {
        "load": "load_norm",
        "requests_per_min": "requests_per_min",
        "error_rate": "error_rate_norm",
    },

}


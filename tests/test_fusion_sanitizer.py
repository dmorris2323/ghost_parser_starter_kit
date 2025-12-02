import pandas as pd

from fusion_sanitizer import sanitize


def test_sanitize_never_negative():
    df = pd.DataFrame(
        {
            "Seismic_Mag": [5.0, -1.0, None],
            "Radiation_uSv": [2.5, -3.0, None],
            "Comms_State": ["Normal", None, "Burst"],
            "AOI_Hit": [True, None, False],
        }
    )

    cleaned = sanitize(df)

    assert (cleaned["Seismic_Mag"] >= 0).all()
    assert (cleaned["Radiation_uSv"] >= 0).all()
    assert cleaned["Comms_State"].isna().sum() == 0
    assert cleaned["AOI_Hit"].isna().sum() == 0


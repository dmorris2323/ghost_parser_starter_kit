from config_guard import run_config_guard


def test_config_guard_runs():
    """
    Smoke test: config_guard should run without raising
    and return a string that includes the header.
    """
    summary = run_config_guard()
    assert isinstance(summary, str)
    assert "GLL CONFIG GUARD — STATUS" in summary


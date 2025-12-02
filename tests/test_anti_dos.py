from anti_dos import classify_traffic


def test_anti_dos_basic_buckets():
    assert classify_traffic(50, 5.0) == "normal"
    assert classify_traffic(350, 8.0) == "suspicious"

    # Very high volume -> suspected DoS
    label = classify_traffic(2000, 1.0)
    assert label in ("dos_suspected", "dos_suspected".upper())


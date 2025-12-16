import json
from spectral_owl_reasoning import write_reasoning_trace


def main():
    cases = [
        {},
        {"fusion_validation": True},
        {"degraded_validation": True},
        {"base_defense": True},
        {
            "fusion_validation": True,
            "degraded_validation": True,
            "base_defense": True,
        },
    ]

    crashes = 0

    for c in cases:
        try:
            write_reasoning_trace(c)
        except Exception as e:
            crashes += 1
            print("CRASH:", e)

    verdict = "PASS" if crashes == 0 else "FAIL"

    out = {
        "verdict": verdict,
        "runs": len(cases),
        "crashes": crashes,
    }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()


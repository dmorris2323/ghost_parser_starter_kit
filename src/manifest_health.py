from sensor_manifest_loader import load_manifest

def run_manifest_health():
    mf = load_manifest()

    if not mf:
        return {"status": "fail", "reason": "manifest_missing"}

    disabled = [k for k,v in mf.items() if v is False]

    return {
        "status": "ok",
        "total": len(mf),
        "disabled": disabled,
        "enabled": [k for k,v in mf.items() if v]
    }

if __name__ == "__main__":
    print(run_manifest_health())


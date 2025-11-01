import sys

REQUIRED = ["pandas", "streamlit", "matplotlib", "tabulate"]

print("Python:", sys.version)
bad = []
for m in REQUIRED:
    try:
        __import__(m)
        print(f"[OK] {m}")
    except Exception as e:
        print(f"[MISS] {m} -> {e}")
        bad.append(m)

if bad:
    raise SystemExit(f"Missing: {', '.join(bad)}")
print("Environment looks good.")

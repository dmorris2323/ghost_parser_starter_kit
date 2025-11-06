import pandas as pd
from pathlib import Path

def score_fusion(fused_file="fused_output.csv"):
    fused_path = Path(fused_file)

    # If file missing, stop gracefully
    if not fused_path.exists():
        print(f"❌ File not found: {fused_path.resolve()}")
        print("➡️  Create fused_output.csv in src/ and rerun.")
        return None

    df = pd.read_csv(fused_path)

    # Give score: AOI_Hit True → high score, else low
    df['Score'] = df.apply(lambda r: 100 if r.get('AOI_Hit', False) else 10, axis=1)

    df_sorted = df.sort_values(by='Score', ascending=False)
    df_sorted.to_csv("scored_output.csv", index=False)
    print(f"✅ Scoring complete — {len(df_sorted)} rows saved to scored_output.csv")
    return df_sorted.head()


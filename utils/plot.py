"""
Benchmark Results Visualization + Winner Detection
==================================================

Adds a composite 'overall_score' for ranking models.
Saves all graphs to ./graph/ folder.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# 📂 Load Data
# =====================================================
file_path = "benchmark_results.csv"
df = pd.read_csv(file_path)

os.makedirs("graph", exist_ok=True)

# Compute averages per model
summary = (
    df.groupby("model", as_index=False)
    .agg({
        "latency_s": "mean",
        "correctness_score": "mean",
        "faithfulness_score": "mean",
        "relevance_score": "mean"
    })
    .round(3)
)

# Normalize latency (lower = better)
summary["norm_latency"] = 1 - (summary["latency_s"] / summary["latency_s"].max())

# Composite overall score (weights adjustable)
summary["overall_score"] = (
    0.4 * summary["correctness_score"]
    + 0.3 * summary["relevance_score"]
    + 0.2 * summary["faithfulness_score"]
    + 0.1 * summary["norm_latency"]
)

summary = summary.sort_values("overall_score", ascending=False).reset_index(drop=True)

print("\n🏆 Model Ranking (by Overall Score):\n", summary[["model", "overall_score"]])

# =====================================================
# 🏅 Plot 1: Overall Winner Chart
# =====================================================
plt.figure(figsize=(8, 5))
bars = plt.barh(summary["model"], summary["overall_score"], color="skyblue")
plt.xlabel("Overall Composite Score")
plt.title("🏆 Model Performance Ranking (Higher = Better)")

# Highlight the best model in green
bars[0].set_color("limegreen")
plt.gca().invert_yaxis()  # Highest on top

# Annotate bars with scores
for bar in bars:
    plt.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
             f"{bar.get_width():.3f}", va="center")

plt.tight_layout()
plt.savefig("graph/overall_ranking.png", dpi=300)
plt.close()
print("✅ Saved: graph/overall_ranking.png")

# =====================================================
# 📦 Print Winner
# =====================================================
winner = summary.iloc[0]
print(f"\n🏆 Clear Winner: {winner['model']} "
      f"(Score: {winner['overall_score']:.3f})\n")

print("All graphs saved in ./graph/")

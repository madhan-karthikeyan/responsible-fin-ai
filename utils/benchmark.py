"""
Benchmark Script for Responsible Financial AI (Local RAG Evaluation)
====================================================================

Lightweight version — removes Prometheus LLM evaluator.
Evaluates QueryEngine using simple semantic similarity & latency metrics.
"""

import os
import time
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from query import QueryEngine  # your RAG engine


def detect_device():
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"🧠 GPU detected: {gpu_name} ({vram_gb:.1f} GB VRAM)")
        return "cuda"
    print("⚙️ No GPU found — using CPU (slow)")
    return "cpu"

device = detect_device()

# =====================================================
# Load Semantic Model for Similarity Scoring
# =====================================================

similarity_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

# =====================================================
# Example Tests
# =====================================================

tests = [
    {
        "query": "What is the role of RBI in controlling inflation?",
        "reference": "The RBI manages inflation using monetary policy tools like repo rate, open market operations, and reserve ratios to control liquidity and stabilize prices.",
    },
    {
        "query": "Explain what a mutual fund is in simple terms.",
        "reference": "A mutual fund pools investors' money to buy diversified assets like stocks or bonds, managed by professionals for shared profit.",
    },
]

# =====================================================
# Evaluation Metrics (Heuristic)
# =====================================================

def semantic_similarity(a: str, b: str) -> float:
    """Compute semantic similarity between response and reference."""
    emb_a = similarity_model.encode(a, convert_to_tensor=True)
    emb_b = similarity_model.encode(b, convert_to_tensor=True)
    return float(util.cos_sim(emb_a, emb_b).item())

def word_overlap(a: str, b: str) -> float:
    """Simple word overlap ratio."""
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return 0.0
    return len(a_words & b_words) / len(a_words | b_words)

# =====================================================
# Benchmark Runner
# =====================================================
def save_results(results, out_path="benchmark_results.csv"):
    df = pd.DataFrame(results)
    df["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    columns = [
        "model",
        "latency_s",
        "correctness_score",
        "faithfulness_score",
        "relevance_score",
        "timestamp"
    ]

    # If file exists → append without header
    if os.path.exists(out_path):
        df.to_csv(out_path, mode="a", index=False, header=False, columns=columns)
        print(f"📎 Appended {len(df)} new rows → {out_path}")
    else:
        df.to_csv(out_path, index=False, header=True, columns=columns)
        print(f"🆕 Created new file with headers → {out_path}")


def run_benchmarks(chunk_size: int = 512):
    query_engine = QueryEngine()
    results = []

    print("\n🚀 Running Local RAG Benchmarks (no Prometheus)...\n")

    for i, test in enumerate(tests, 1):
        query = test["query"]
        reference = test["reference"]
        print(f"--- Test {i}/{len(tests)}: {query[:80]} ---")

        # Run query
        start = time.time()
        response = query_engine.query(query)
        latency = round(time.time() - start, 2)

        response_text = str(response)
        if len(response_text) > chunk_size:
            response_text = response_text[:chunk_size] + "..."

        # Compute scores
        try:
            correctness = semantic_similarity(response_text, reference)
            faithfulness = word_overlap(response_text, reference)
            relevance = semantic_similarity(response_text, query)
        except Exception as e:
            print(f"⚠️ Evaluation failed: {e}")
            correctness = faithfulness = relevance = 0.0

                
        results.append({
            "model": query_engine.get_model_name(),
            "latency_s": latency,
            "correctness_score": round(correctness, 3),
            "faithfulness_score": round(faithfulness, 3),
            "relevance_score": round(relevance, 3)
        })

        torch.cuda.empty_cache()

    # Save all results
    save_results(results)

# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":
    run_benchmarks()

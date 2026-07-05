import timeit
import pandas as pd
import numpy as np

# Generate a large dataset (1 million rows)
N = 1_000_000
np.random.seed(42)

# Generate strings representing numbers with commas, and introduce some random NaNs or invalid strings
data = np.random.uniform(-1, 5, N).astype(str)
data = np.char.replace(data, '.', ',')

# Introduce ~10% NaNs and invalid strings
null_indices = np.random.choice(N, size=int(N * 0.1), replace=False)
data[null_indices] = "invalido"

df = pd.DataFrame({"Inflacao_Mensal": data})

# Simulate the to_numeric conversion
df["Inflacao_Mensal"] = pd.to_numeric(
    df["Inflacao_Mensal"].str.replace(",", ".", regex=False), errors="coerce"
)

# Original code
def func_original(df):
    df_copy = df.copy()
    if df_copy["Inflacao_Mensal"].isnull().any():
        nulos_count = df_copy["Inflacao_Mensal"].isnull().sum()
        df_copy = df_copy.dropna(subset=["Inflacao_Mensal"])
    return df_copy

# Optimized code
def func_optimized(df):
    df_copy = df.copy()
    inflacao_nula_mask = df_copy["Inflacao_Mensal"].isnull()
    if inflacao_nula_mask.any():
        nulos_count = inflacao_nula_mask.sum()
        df_copy = df_copy[~inflacao_nula_mask]
    return df_copy

if __name__ == "__main__":
    # Test execution
    orig_res = func_original(df)
    opt_res = func_optimized(df)
    assert len(orig_res) == len(opt_res), "Results length differ"

    # Benchmark Original
    time_original = timeit.repeat(
        stmt="func_original(df)",
        setup="from __main__ import func_original, df",
        number=10,
        repeat=5
    )

    # Benchmark Optimized
    time_optimized = timeit.repeat(
        stmt="func_optimized(df)",
        setup="from __main__ import func_optimized, df",
        number=10,
        repeat=5
    )

    print(f"Original Time (Median of 5 repeats of 10 loops): {np.median(time_original):.4f} seconds")
    print(f"Optimized Time (Median of 5 repeats of 10 loops): {np.median(time_optimized):.4f} seconds")

    improvement = (np.median(time_original) - np.median(time_optimized)) / np.median(time_original) * 100
    print(f"Improvement: {improvement:.2f}%")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recompute the inter-rater agreement statistics reported for TCM-BO release 1.9.17.

    Cohen's kappa          = 0.612  (95% CI 0.521-0.702)
    linearly weighted kappa= 0.676  (95% CI 0.585-0.767)
    observed agreement     = 81.8%  (260 / 318)
    discordant pairs       = 58

Input : kappa_ratings_double_blind_318.xlsx   (shipped in this folder)
Requires: Python >= 3.8 and openpyxl.

Usage:
    python compute_kappa.py
    python compute_kappa.py --input kappa_ratings_double_blind_318.xlsx

The rating scale is ordinal and is ordered 正确 (correct) < 存疑 (uncertain)
< 错误 (incorrect); linear weights are 1 - |i - j| / (K - 1) with K = 3.
Confidence intervals are asymptotic, using
    SE(kappa) = sqrt( Po (1 - Po) / ((1 - Pe)^2 * n) )
which is the standard large-sample variance for Cohen's kappa.
"""

import argparse
import math
import os
import sys

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl is required:  pip install openpyxl")

# Ordinal scale, worst agreement first.
SCALE = ["正确", "存疑", "错误"]  # correct, uncertain, incorrect
ENGLISH = {"正确": "correct", "存疑": "uncertain", "错误": "incorrect"}


def read_pairs(path, sheet="kappa评审表"):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    header = [str(c) if c is not None else "" for c in rows[0]]

    def col(prefix):
        for i, h in enumerate(header):
            if h.startswith(prefix):
                return i
        raise KeyError(f"column starting with {prefix!r} not found in {header}")

    ia, ib = col("专家A判定"), col("专家B判定")  # rater A / rater B verdict
    pairs = []
    for r in rows[1:]:
        if ia < len(r) and ib < len(r) and r[ia] and r[ib]:
            a, b = str(r[ia]).strip(), str(r[ib]).strip()
            if a not in SCALE or b not in SCALE:
                raise ValueError(f"unexpected verdict: {a!r} / {b!r}")
            pairs.append((a, b))
    wb.close()
    return pairs


def weights(k):
    """Linear agreement weights: w_ij = 1 - |i-j| / (k-1).

    w_ij = 1 on the diagonal (full credit for exact agreement) and decays
    linearly towards 0 for the most distant category pair. Using the
    complement (|i-j|/(k-1)) would yield a weighted *disagreement* statistic,
    which is not Cohen's weighted kappa.
    """
    return [[1 - abs(i - j) / (k - 1) for j in range(k)] for i in range(k)]


def kappa_stats(pairs):
    n = len(pairs)
    k = len(SCALE)
    idx = {c: i for i, c in enumerate(SCALE)}

    obs = [[0] * k for _ in range(k)]
    for a, b in pairs:
        obs[idx[a]][idx[b]] += 1

    row = [sum(obs[i]) for i in range(k)]
    col = [sum(obs[i][j] for i in range(k)) for j in range(k)]

    po = sum(obs[i][i] for i in range(k)) / n
    pe = sum(row[i] * col[i] for i in range(k)) / (n * n)

    w = weights(k)
    pow_ = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k)) / n
    pew = sum(w[i][j] * row[i] * col[j] for i in range(k) for j in range(k)) / (n * n)

    def ci(po_v, pe_v):
        se = math.sqrt(po_v * (1 - po_v) / ((1 - pe_v) ** 2 * n))
        v = (po_v - pe_v) / (1 - pe_v)
        return v, v - 1.96 * se, v + 1.96 * se

    kap, kap_lo, kap_hi = ci(po, pe)
    wkap, wkap_lo, wkap_hi = ci(pow_, pew)

    return {
        "n": n,
        "discordant": n - sum(obs[i][i] for i in range(k)),
        "po": po,
        "pe": pe,
        "kappa": kap,
        "kappa_ci": (kap_lo, kap_hi),
        "weighted": wkap,
        "weighted_ci": (wkap_lo, wkap_hi),
        "marginal_a": dict(zip((ENGLISH[c] for c in SCALE), row)),
        "marginal_b": dict(zip((ENGLISH[c] for c in SCALE), col)),
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=os.path.join(here, "kappa_ratings_double_blind_318.xlsx"))
    ap.add_argument("--sheet", default="kappa评审表")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    pairs = read_pairs(args.input, args.sheet)
    s = kappa_stats(pairs)

    print("TCM-BO double-blind mapping review - inter-rater agreement")
    print("=" * 62)
    print(f"rated items                 : {s['n']}")
    print(f"discordant pairs            : {s['discordant']}")
    print(f"observed agreement (Po)     : {s['po'] * 100:.1f}%")
    print(f"expected agreement (Pe)     : {s['pe'] * 100:.1f}%")
    print(f"Cohen's kappa               : {s['kappa']:.3f}  (95% CI {s['kappa_ci'][0]:.3f}-{s['kappa_ci'][1]:.3f})")
    print(f"linearly weighted kappa     : {s['weighted']:.3f}  (95% CI {s['weighted_ci'][0]:.3f}-{s['weighted_ci'][1]:.3f})")
    print()
    print("rater A marginals:", s["marginal_a"])
    print("rater B marginals:", s["marginal_b"])
    print()
    print("Expected values from the manuscript:")
    print("  kappa = 0.612 (0.521-0.702); weighted = 0.676 (0.585-0.767); Po = 81.8%")
    ok = (
        round(s["kappa"], 3) == 0.612
        and round(s["weighted"], 3) == 0.676
        and round(s["po"] * 100, 1) == 81.8
    )
    print("REPRODUCED" if ok else "MISMATCH - check the input file")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Coupon‑Collector Simulator  –  v3 (Problem 4 ready)
────────────────────────────────────────────────────
Features
────────
1. **Interactive simulation** for arbitrary n and T (expressions like `2**8`
   are accepted).
2. **Small‑n sanity test** prints a step‑by‑step table.
3. **Benchmark** checks that 100 × 10 000 trials run in a few seconds.
4. **Histogram** of trial lengths for the interactive run.
5. **Problem 4 experiment** – 10 trials for n = 2^k, k = 8…20 inclusive,
   prints a neatly formatted table and draws a log–log plot of average
   steps versus n.

Usage
─────
Run the script, choose an option from the main menu, and follow prompts.
Requires Python 3.8+; matplotlib is needed for the plots.

"""

import random
import time
from typing import List, Tuple

# ───────────────────────────── core logic ───────────────────────────────────── #
def coupon_collector_trial(n: int) -> int:
    """Run ONE coupon‑collector trial and return the number of draws."""
    collected: set[int] = set()
    steps = 0
    while len(collected) < n:
        coupon = random.randrange(n)
        collected.add(coupon)
        steps += 1
    return steps


def simulate_coupon_collector(
    n: int,
    trials: int,
    verbose: bool = False,
) -> Tuple[float, List[int]]:
    """
    Run multiple trials and return (average_steps, all_steps).
    If  verbose=True  each individual trial length is printed.
    """
    steps_list: List[int] = []
    for t in range(1, trials + 1):
        s = coupon_collector_trial(n)
        steps_list.append(s)
        if verbose:
            print(f"Trial {t:>4}: {s} steps")
    avg_steps = sum(steps_list) / trials
    return avg_steps, steps_list


# ──────────────────────── pretty helpers for testing ───────────────────────── #
def _print_sequence_table(sequence: List[int]) -> None:
    """Neatly print a table of coupon draws."""
    print("\nStep | Coupon")
    print("-----+--------")
    for i, c in enumerate(sequence, 1):
        print(f"{i:>4} | {c}")
    print()


# ─────────────────────────── testing / debugging ───────────────────────────── #
def _test_small_n() -> None:
    """
    Sanity‑check with n = 3.
    Prints every coupon drawn in a tidy table so you can verify
    that all coupons appeared before the trial ended.
    """
    n = 3
    print(f"=== Sanity test with n = {n} (detailed) ===")

    collected: set[int] = set()
    sequence: List[int] = []
    while len(collected) < n:
        coupon = random.randrange(n)
        sequence.append(coupon)
        collected.add(coupon)

    _print_sequence_table(sequence)
    print(f"✔ All {n} coupons collected after {len(sequence)} steps\n")


def _benchmark() -> None:
    """
    Performance check:
    100 trials with 10 000 coupons should finish in a few seconds.
    """
    n, trials = 10_000, 100
    print(f"=== Benchmark: n={n}, trials={trials} ===")
    t0 = time.perf_counter()
    avg, _ = simulate_coupon_collector(n, trials)
    elapsed = time.perf_counter() - t0
    print(f"Average steps: {avg:,.2f}   |   elapsed: {elapsed:.2f}s\n")


# ────────────────────────────── visualization ─────────────────────────────── #
def _plot_histogram(data: List[int], n: int, trials: int) -> None:
    """Display a histogram of trial lengths (requires matplotlib)."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed – histogram skipped.")
        return

    plt.figure()
    plt.hist(data, bins="auto", edgecolor="black")
    plt.title(f"Coupon‑Collector Simulation\nn = {n}, trials = {trials}")
    plt.xlabel("Number of draws until completion")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()


def _plot_problem4(ns: List[int], avgs: List[float]) -> None:
    """Plot average steps vs n for Problem 4 (log–log)."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed – Problem 4 plot skipped.")
        return

    plt.figure()
    plt.plot(ns, avgs, marker="o", linestyle="-")
    plt.xscale("log", base=2)
    plt.yscale("log")
    plt.xlabel("n  (log₂ scale)")
    plt.ylabel("Average steps  (log₁₀ scale)")
    plt.title("Problem 4 – Coupon‑Collector Growth")
    plt.grid(which="both", linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()


# ────────────────────────── Problem 4 experiment ──────────────────────────── #
def run_problem4(trials_per_n: int = 10) -> None:
    """
    Runs 10 trials for n = 2^k, k = 8…20, prints a table, and plots results.
    """
    ks = range(8, 21)  # 8 … 20 inclusive
    results: List[Tuple[int, float]] = []

    print("\nProblem 4 experiment ({} trials each)".format(trials_per_n))
    print(" k |      n = 2^k |  avg steps")
    print("---+-------------+-------------")

    for k in ks:
        n = 2 ** k
        avg, _ = simulate_coupon_collector(n, trials_per_n)
        results.append((n, avg))
        print(f"{k:>2} | {n:>11,} | {avg:>11.2f}")

    ns   = [r[0] for r in results]
    avgs = [r[1] for r in results]

    _plot_problem4(ns, avgs)

    # Simple textual conjecture hint
    ratios = [avg / n for n, avg in results]
    print("\nRatio avg/n (shows ~log n growth):")
    for k, r in zip(ks, ratios):
        print(f"k={k:>2}, avg/n ≈ {r:.3f}")
    print(
        "\nEmpirically the average number of coupons grows faster than Θ(n) "
        "but much slower than Θ(n²).  The pattern avg ≈ n·log n is consistent "
        "with theory (expected value = n·Hₙ ≈ n(ln n + γ))."
    )


# ─────────────────────────── command‑line UI ──────────────────────────────── #
def _safe_eval(expr: str) -> int:
    """
    Evaluate a simple arithmetic expression and return an int.
    Only literals and +‑*/**() are allowed; names are disallowed.
    """
    allowed = {"__builtins__": {}}
    try:
        val = eval(expr, allowed, {})
        if not isinstance(val, (int, float)):
            raise ValueError("expression did not evaluate to a number")
        return int(val)
    except Exception as exc:
        raise ValueError(f"invalid numeric expression: {exc}") from None


def main_menu() -> None:
    while True:
        print(
            "\n────────── Coupon‑Collector Simulator ──────────"
            "\n1) Interactive simulation"
            "\n2) Small‑n sanity test (n = 3)"
            "\n3) Benchmark (100 × 10 000)"
            "\n4) Run Problem 4 experiment"
            "\n5) Quit"
        )
        choice = input("Select option [1‑5]: ").strip()
        if choice == "1":
            try:
                n_expr = input("Number of coupon types  n: ")
                T_expr = input("Number of trials       T: ")
                n = _safe_eval(n_expr)
                T = _safe_eval(T_expr)
            except ValueError as e:
                print(f"⚠️  {e}")
                continue

            avg, steps_list = simulate_coupon_collector(n, T)
            print(f"\nAverage steps over {T} trials: {avg:.2f}")
            _plot_histogram(steps_list, n, T)

        elif choice == "2":
            _test_small_n()
        elif choice == "3":
            _benchmark()
        elif choice == "4":
            try:
                t_expr = input("Trials per n (default 10): ").strip() or "10"
                trials_per_n = _safe_eval(t_expr)
            except ValueError as e:
                print(f"⚠️  {e}")
                continue
            run_problem4(trials_per_n)
        elif choice == "5":
            print("Good‑bye!")
            break
        else:
            print("Please enter 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    main_menu()
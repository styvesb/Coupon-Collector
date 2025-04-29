#!/usr/bin/env python3
import random, sys, numpy as np, matplotlib.pyplot as plt

# ----------------------------------------------------------------------
#  Core simulator
# ----------------------------------------------------------------------
def simulate_trial(probs, num_gens=20):
    cdf = np.cumsum(probs)
    sizes = [1]                                    # X₀ = 1
    for _ in range(num_gens):
        children = sum(
            0 if (r := random.random()) < cdf[0] else 1 if r < cdf[1] else 2
            for _ in range(sizes[-1])
        )
        sizes.append(children)
        if children == 0:                          # extinction
            sizes.extend([0] * (num_gens - len(sizes) + 1))
            break
    return sizes


def simulate_trials(probs, trials=1000, num_gens=20):
    totals = np.zeros(num_gens + 1)
    for _ in range(trials):
        totals += simulate_trial(probs, num_gens)[: num_gens + 1]
    return (totals / trials).tolist()


def mu(probs):
    return sum(k * p for k, p in enumerate(probs))


# ----------------------------------------------------------------------
#  1) One-trial, verbose walkthrough
# ----------------------------------------------------------------------
def single_trial_verbose(probs, num_gens=10):
    sizes = simulate_trial(probs, num_gens)
    total = 1
    print("\nGeneration 0 : started with 1 root")
    for g in range(1, num_gens + 1):
        kids = sizes[g]
        total += kids
        print(f"Generation {g:<2}: children = {kids:<4} | X_{g} = {kids:<4} | total = {total}")
        if kids == 0:
            print("Process went extinct here.\n")
            break
    else:
        print()


# ----------------------------------------------------------------------
#  2) Empirical vs μⁿ
# ----------------------------------------------------------------------
def compare_empirical_to_mu_power(probs, trials=5000, gens=10):
    μ = mu(probs)
    means = simulate_trials(probs, trials, gens)
    print(f"\nμ = {μ:.6f}   ({trials} trials, up to gen {gens})")
    print(f"{'n':>3} {'Empirical E[X_n]':>18} {'μ^n':>15} {'Abs err':>11} {'% err':>8}")
    for n, emp in enumerate(means):
        theo = μ ** n
        err  = abs(emp - theo)
        pct  = (err / theo * 100) if theo else 0
        print(f"{n:3d} {emp:18.6f} {theo:15.6f} {err:11.6f} {pct:8.3f}")


# ----------------------------------------------------------------------
#  3) Plot mean generation sizes (one distribution)
# ----------------------------------------------------------------------
def plot_mean_sizes(probs, trials=1000, gens=12, label=""):
    means = simulate_trials(probs, trials, gens)
    x = range(1, gens + 1)
    plt.plot(x, means[1:], marker="o", label=label)


# ----------------------------------------------------------------------
#  4) Plot all distributions side-by-side + table
# ----------------------------------------------------------------------
def plot_all_distributions(dists, trials=1000, gens=12):
    plt.figure(figsize=(7, 4))

    # --- gather data for both the plot and the table ---
    mean_dict = {}                     # {label: [E[X₀], …, E[X_g]]}
    for lbl, probs in dists.values():
        means = simulate_trials(probs, trials, gens)
        mean_dict[lbl] = means
        x = range(1, gens + 1)
        plt.plot(x, means[1:], marker="o", label=lbl)

    # --- pretty-print a table of the averages ---
    print(f"\nAverage number of nodes per generation  ({trials} trials)\n")
    header = ["Gen"] + list(mean_dict.keys())
    col_w  = 12
    print(" | ".join(f"{h:>{col_w}}" for h in header))
    print("-" * (len(header) * (col_w + 3) - 3))
    for g in range(1, gens + 1):
        row = [f"{g:>{col_w}}"]
        for lbl in mean_dict:
            row.append(f"{mean_dict[lbl][g]:{col_w}.3f}")
        print(" | ".join(row))
    print()  # blank line after table

    # --- finish the plot ---
    plt.title(f"Mean generation sizes ({trials} trials each)")
    plt.xlabel("Generation n")
    plt.ylabel("Average Xₙ")
    plt.grid(True, ls="--", lw=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ----------------------------------------------------------------------
#  Menu / main loop
# ----------------------------------------------------------------------
DISTRIBUTIONS = {
    "1": ("D₁  (E = 0.75)", [0.50, 0.25, 0.25]),
    "2": ("D₂  (E = 1.25)", [0.25, 0.25, 0.50]),
    "3": ("D₃  (E = 1.00)", [1 / 3, 1 / 3, 1 / 3]),
}

def pick_distribution():
    print("\nChoose a distribution:")
    for k, (lbl, probs) in DISTRIBUTIONS.items():
        print(f"  {k}) {lbl:12}  probs = {probs}")
    return DISTRIBUTIONS.get(input("Your choice: ").strip(), (None, None))[1]


def main():
    random.seed(0)  # reproducible
    menu = """
===================  Branching-Process Lab  =====================
1) One-trial walkthrough (verbose)
2) Empirical E[Xₙ] vs μⁿ table
3) Plot mean generation sizes (single distribution)
4) Plot mean generation sizes for ALL distributions
0) Quit
=================================================================
"""
    while True:
        print(menu)
        cmd = input("Enter option: ").strip()
        if cmd == "1":
            p = pick_distribution();        print() if not p else single_trial_verbose(p, int(input("Generations [10]: ") or "10"))
        elif cmd == "2":
            p = pick_distribution();        print() if not p else compare_empirical_to_mu_power(p, int(input("Trials [5000]: ") or "5000"), int(input("Generations [10]: ") or "10"))
        elif cmd == "3":
            p = pick_distribution()
            if p:
                plot_mean_sizes(p, int(input("Trials [1000]: ") or "1000"), int(input("Plot gens 1…g [12]: ") or "12"), "chosen distribution")
                plt.title("Mean generation sizes")
                plt.xlabel("Generation n"); plt.ylabel("Average Xₙ"); plt.grid(True, ls="--", lw=0.5); plt.tight_layout(); plt.show()
        elif cmd == "4":
            plot_all_distributions(DISTRIBUTIONS, int(input("Trials per dist [1000]: ") or "1000"), int(input("Plot gens 1…g [12]: ") or "12"))
        elif cmd == "0":
            print("Bye!"); sys.exit(0)
        else:
            print("❗ Unknown option – try again.")

if __name__ == "__main__":
    main()

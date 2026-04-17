import random
import time
import statistics
import matplotlib.pyplot as plt
import argparse


# ── Sorting Algorithms ──────────────────────────────────────────────

def bubble_sort(arr):
    a = arr[:]
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def insertion_sort(arr):
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(arr):
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ── Helpers ──────────────────────────────────────────────────────────

def generate_random_array(size, lower_bound=0, upper_bound=1_000_000):
    return [random.randint(lower_bound, upper_bound) for _ in range(size)]


def generate_nearly_sorted_array(size, noise_percent):
    """Part C: Starts with a sorted array and adds noise"""
    arr = list(range(size))
    num_swaps = int(size * (noise_percent / 100))
    for _ in range(num_swaps):
        idx1 = random.randint(0, size - 1)
        idx2 = random.randint(0, size - 1)
        arr[idx1], arr[idx2] = arr[idx2], arr[idx1]
    return arr


def time_sort(sort_fn, arr):
    start = time.perf_counter()
    sort_fn(arr)
    end = time.perf_counter()
    return end - start


# ── Visualization ────────────────────────────────────────────────────

def plot_results(results, filename):
    """Generates and saves the required plots"""
    plt.figure(figsize=(12, 7))
    markers = {"Bubble Sort": "o", "Insertion Sort": "s", "Merge Sort": "^"}

    for name, data in results.items():
        if not data["sizes"]:
            continue
        plt.errorbar(data["sizes"], data["avg"], yerr=data["std"],
                     label=name, marker=markers.get(name, "d"), capsize=4)

    plt.xlabel("Array Size (n)", fontsize=12)
    plt.ylabel("Running Time (seconds)", fontsize=12)
    plt.title(f"Sorting Performance ({filename})", fontsize=14)
    plt.xscale("log")
    plt.yscale("log")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    print(f"\nPlot saved as {filename}")


# ── Experiment Runner ────────────────────────────────────────────────

def run_sorting_experiment(algorithms, sizes, num_runs, experiment_type, filename):
    results = {name: {"sizes": [], "avg": [], "std": []} for name in algorithms}
    quadratic_limit = 50_000

    for size in sizes:
        if experiment_type == 0:
            arrays = [generate_random_array(size) for _ in range(num_runs)]
        else:
            noise = 5 if experiment_type == 1 else 20
            arrays = [generate_nearly_sorted_array(size, noise) for _ in range(num_runs)]

        for name, sort_fn in algorithms.items():
            if name in ("Bubble Sort", "Insertion Sort") and size > quadratic_limit:
                print(f"  Skipping {name} for size {size:>10,} (too slow)")
                continue

            times = [time_sort(sort_fn, arr) for arr in arrays]

            avg = statistics.mean(times)
            std = statistics.stdev(times) if num_runs > 1 else 0.0

            results[name]["sizes"].append(size)
            results[name]["avg"].append(avg)
            results[name]["std"].append(std)

            print(f"Size: {size:>10,} | {name:<16} | Avg: {avg:.6f}s | Std: {std:.6f}s")

    plot_results(results, filename)


# ── Main / CLI ───────────────────────────────────────────────────────

def main():
    ALGO_MAP = {
        1: ("Bubble Sort", bubble_sort),
        3: ("Insertion Sort", insertion_sort),
        4: ("Merge Sort", merge_sort)
    }

    parser = argparse.ArgumentParser(description="Sorting Experiment UI")
    parser.add_argument("-a", nargs="+", type=int, required=True, help="Algorithm IDs (1, 3, 4)")
    parser.add_argument("-s", nargs="+", type=int, required=True, help="Array sizes")
    parser.add_argument("-e", type=int, choices=[0, 1, 2], default=0, help="0:Random, 1:5% noise, 2:20% noise")
    parser.add_argument("-r", type=int, default=3, help="Repetitions")

    args = parser.parse_args()

    selected_algos = {ALGO_MAP[i][0]: ALGO_MAP[i][1] for i in args.a if i in ALGO_MAP}
    filename = "result1.png" if args.e == 0 else "result2.png"

    run_sorting_experiment(selected_algos, args.s, args.r, args.e, filename)


if __name__ == "__main__":
    main()
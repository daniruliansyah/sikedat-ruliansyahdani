import csv
import os
from collections import Counter

INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'labeled_frekuensi-cyclefailure', 'sorted.csv')


def percentile_linear(data, p):
    """Persentil ke-p dengan interpolasi linear (setara numpy default)."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    idx = (p / 100) * (n - 1)
    lo = int(idx)
    hi = lo + 1
    frac = idx - lo
    if hi >= n:
        return float(sorted_data[lo])
    return sorted_data[lo] + frac * (sorted_data[hi] - sorted_data[lo])


def main():
    rows = []
    with open(INPUT_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    densities = [int(row['Tingkat_Kepadatan']) for row in rows]
    n = len(densities)

    p33 = percentile_linear(densities, 33)
    p66 = percentile_linear(densities, 66)

    print("=" * 55)
    print("  HASIL PERHITUNGAN PERSENTIL - Tingkat_Kepadatan")
    print("=" * 55)
    print(f"  Total data       : {n} baris")
    print(f"  Nilai minimum    : {min(densities)}")
    print(f"  Nilai maksimum   : {max(densities)}")
    print()
    print(f"  Persentil 33     : {p33:.4f}")
    print(f"  Persentil 66     : {p66:.4f}")
    print()
    print("  THRESHOLD KLASIFIKASI 3 KELAS:")
    print(f"  Rendah  :  Tingkat_Kepadatan <  {p33:.4f}  (< {p33})")
    print(f"  Sedang  :  Tingkat_Kepadatan >= {p33:.4f} dan <= {p66:.4f}")
    print(f"  Tinggi  :  Tingkat_Kepadatan >  {p66:.4f}  (> {p66})")
    print()

    rendah = sum(1 for d in densities if d < p33)
    sedang = sum(1 for d in densities if p33 <= d <= p66)
    tinggi = sum(1 for d in densities if d > p66)

    print("  DISTRIBUSI SETELAH KLASIFIKASI:")
    print(f"  Rendah  : {rendah:4d} baris  ({rendah / n * 100:.1f}%)")
    print(f"  Sedang  : {sedang:4d} baris  ({sedang / n * 100:.1f}%)")
    print(f"  Tinggi  : {tinggi:4d} baris  ({tinggi / n * 100:.1f}%)")
    print()

    freq = Counter(sorted(densities))
    print("  FREKUENSI TIAP NILAI Tingkat_Kepadatan:")
    for val in sorted(freq.keys()):
        bar = "#" * (freq[val] // 5)
        label = "Rendah" if val < p33 else ("Sedang" if val <= p66 else "Tinggi")
        print(f"    nilai {val:2d}  : {freq[val]:4d} kali  {bar}  [{label}]")
    print("=" * 55)


if __name__ == '__main__':
    main()

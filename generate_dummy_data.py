"""
generate_dummy_data.py
======================
Generate dataset dummy 672 baris untuk testing pipeline SIKEDAT.

Struktur: 14 hari x 8 jam x 6 interval = 672 baris
- 14 hari = 7 hari (Sen-Min) x 2 pengulangan
- 8 jam   = pagi (06,07,08) + sore (15,16,17,18,19)
- 6 interval per jam = menit 10,20,30,40,50,60

Label tingkat_kepadatan:
- Rendah : total < 50
- Sedang : 50 <= total <= 85
- Tinggi : total > 85
"""

import random
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

HARI_LIST   = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
JAM_LIST    = [6, 7, 8, 15, 16, 17, 18, 19]
MENIT_LIST  = [10, 20, 30, 40, 50, 60]
PENGULANGAN = 2

# Profil volume per jam: (mean, std) untuk motor/mobil/bus/truk
PROFIL = {
    6:  {'motor':(28,6),  'mobil':(9,3),  'bus':(3,1), 'truk':(2,1)},
    7:  {'motor':(72,12), 'mobil':(22,5), 'bus':(6,2), 'truk':(4,2)},
    8:  {'motor':(48,10), 'mobil':(15,4), 'bus':(4,2), 'truk':(3,1)},
    15: {'motor':(38,8),  'mobil':(12,3), 'bus':(4,1), 'truk':(3,1)},
    16: {'motor':(55,10), 'mobil':(17,4), 'bus':(5,2), 'truk':(3,1)},
    17: {'motor':(78,13), 'mobil':(24,5), 'bus':(7,2), 'truk':(4,2)},
    18: {'motor':(52,10), 'mobil':(16,4), 'bus':(5,2), 'truk':(3,1)},
    19: {'motor':(32,7),  'mobil':(10,3), 'bus':(3,1), 'truk':(2,1)},
}

# Faktor pengali per hari
FAKTOR_HARI = {
    'Senin':1.05, 'Selasa':1.00, 'Rabu':1.02,
    'Kamis':1.00, 'Jumat':1.10, 'Sabtu':0.85, 'Minggu':0.75
}

def gen(mean, std, faktor=1.0):
    return max(0, int(round(np.random.normal(mean * faktor, std))))

def label(total):
    if total < 50:  return 'Rendah'
    if total <= 85: return 'Sedang'
    return 'Tinggi'

rows = []
for _ in range(PENGULANGAN):
    for hari in HARI_LIST:
        f = FAKTOR_HARI[hari]
        for jam in JAM_LIST:
            p = PROFIL[jam]
            for menit in MENIT_LIST:
                motor = gen(*p['motor'], f)
                mobil = gen(*p['mobil'], f)
                bus   = gen(*p['bus'],   f)
                truk  = gen(*p['truk'],  f)
                total = motor + mobil + bus + truk
                rows.append({
                    'hari': hari, 'jam': jam, 'menit': menit,
                    'motor': motor, 'mobil': mobil, 'bus': bus, 'truk': truk,
                    'total_kendaraan': total, 'tingkat_kepadatan': label(total)
                })

df = pd.DataFrame(rows)
assert len(df) == 672, f"Jumlah baris: {len(df)}"

print(f"Dataset: {len(df)} baris")
print(df['tingkat_kepadatan'].value_counts().to_string())
print(df.head(3).to_string(index=False))

df.to_csv('dataset_dummy_berlabel.csv', index=False)
df.drop(columns=['tingkat_kepadatan']).to_csv('dataset_dummy_input.csv', index=False)
print("\nFile tersimpan: dataset_dummy_berlabel.csv & dataset_dummy_input.csv")
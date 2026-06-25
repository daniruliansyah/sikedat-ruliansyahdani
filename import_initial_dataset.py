"""
import_initial_dataset.py
=========================
Script satu kali jalan: impor 877 baris dari dataset_real_berlabel.csv
ke tabel dataset di sikedat.db dengan status_validasi='validated'.

Jalankan setelah menghapus data dummy dari DB:
    python import_initial_dataset.py
"""

import os, sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import pandas as pd
from app import app, db
from models import Dataset

CSV_PATH = os.path.join(BASE_DIR, 'dataset_real_berlabel.csv')


def main():
    df = pd.read_csv(CSV_PATH)
    print(f'Membaca {len(df)} baris dari {CSV_PATH}')
    print(df['Tingkat_Kepadatan'].value_counts().to_string())

    now      = datetime.now()
    inserted = 0

    with app.app_context():
        for _, row in df.iterrows():
            record = Dataset(
                hari              = str(row['Hari']),
                jam               = int(row['Jam']),
                menit             = int(row['Menit']),
                motor             = int(row['Motor']),
                mobil             = int(row['Mobil']),
                bus               = int(row['Bus']),
                truk              = int(row['Truk']),
                total_kendaraan   = int(row['Total_Kendaraan']),
                tingkat_kepadatan = str(row['Tingkat_Kepadatan']),
                label_final       = str(row['Tingkat_Kepadatan']),
                status_validasi   = 'validated',
                nama_file         = 'dataset_real_berlabel.csv',
                tanggal           = None,
                batch_id          = None,
                classified_by     = None,
                validated_by      = None,
                created_at        = now,
                validated_at      = now,
            )
            db.session.add(record)
            inserted += 1

        db.session.commit()

    print(f'\n{inserted} baris berhasil diimpor ke database.')
    print('Selesai!')


if __name__ == '__main__':
    main()

"""
migrate_db.py
=============
Tambahkan kolom baru ke tabel dataset yang sudah ada:
- tanggal   (DATE)
- batch_id  (VARCHAR 40)

Jalankan SEKALI setelah update models.py:
    python migrate_db.py
"""

import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'sikedat.db')

if not os.path.exists(DB_PATH):
    print("Database belum ada. Jalankan app.py dulu sekali agar DB terbuat.")
    exit()

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

# Cek kolom yang sudah ada
cur.execute("PRAGMA table_info(dataset)")
existing = {row[1] for row in cur.fetchall()}
print(f"Kolom yang sudah ada: {existing}")

added = []

if 'tanggal' not in existing:
    cur.execute("ALTER TABLE dataset ADD COLUMN tanggal DATE")
    added.append('tanggal')

if 'batch_id' not in existing:
    cur.execute("ALTER TABLE dataset ADD COLUMN batch_id VARCHAR(40)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_dataset_batch_id ON dataset(batch_id)")
    added.append('batch_id')

conn.commit()
conn.close()

if added:
    print(f"Kolom berhasil ditambahkan: {added}")
else:
    print("Tidak ada kolom yang perlu ditambahkan (sudah up-to-date).")
print("Migrasi selesai.")
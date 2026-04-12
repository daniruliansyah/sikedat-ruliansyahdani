# models.py
# Definisi semua tabel database SIKEDAT
# menggunakan Flask-SQLAlchemy (sesuai proposal BAB 2.11.8)

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db    = SQLAlchemy()
bcrypt = Bcrypt()


# ============================================================
# TABEL 1: roles
# Menyimpan daftar role/jabatan yang ada di sistem
# ============================================================
class Role(db.Model):
    __tablename__ = 'roles'

    id          = db.Column(db.Integer, primary_key=True)
    nama        = db.Column(db.String(50), unique=True, nullable=False)
    # Deskripsi singkat role ini untuk apa
    deskripsi   = db.Column(db.String(200), nullable=True)
    # Apakah role ini punya akses ke halaman restricted
    # (classifier, validasi, retrain_model)
    akses_penuh = db.Column(db.Boolean, default=False, nullable=False)

    # Relasi ke users
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.nama}>'


# ============================================================
# TABEL 2: users
# Menyimpan data akun pengguna sistem
# ============================================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80), unique=True, nullable=False)
    password     = db.Column(db.String(200), nullable=False)  # disimpan ter-hash
    nama_lengkap = db.Column(db.String(150), nullable=True)
    role_id      = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi ke dataset (sebagai pengklasifikasi)
    dataset_diklasifikasi = db.relationship(
        'Dataset',
        foreign_keys='Dataset.classified_by',
        backref='pengklasifikasi',
        lazy=True
    )
    # Relasi ke dataset (sebagai validator)
    dataset_divalidasi = db.relationship(
        'Dataset',
        foreign_keys='Dataset.validated_by',
        backref='validator',
        lazy=True
    )
    # Relasi ke retrain_history
    retrain_dilakukan = db.relationship(
        'RetrainHistory',
        backref='operator',
        lazy=True
    )

    # Helper: cek apakah user punya akses penuh
    @property
    def has_full_access(self):
        return self.role.akses_penuh if self.role else False

    def set_password(self, plain_password):
        self.password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    def check_password(self, plain_password):
        return bcrypt.check_password_hash(self.password, plain_password)

    def __repr__(self):
        return f'<User {self.username}>'


# ============================================================
# TABEL 3: dataset
# Menyimpan data hasil ekstraksi YOLOv8 yang sudah diklasifikasi
# dan proses validasi Human-in-the-Loop (sesuai proposal BAB 2.10)
# ============================================================
class Dataset(db.Model):
    __tablename__ = 'dataset'

    id                = db.Column(db.Integer, primary_key=True)
    hari              = db.Column(db.String(10),  nullable=False)   # Senin–Minggu
    jam               = db.Column(db.Integer,     nullable=False)   # 6–20
    menit             = db.Column(db.Integer,     nullable=False)   # 10,20,30,...,60
    motor             = db.Column(db.Integer,     nullable=False)
    mobil             = db.Column(db.Integer,     nullable=False)
    bus               = db.Column(db.Integer,     nullable=False)
    truk              = db.Column(db.Integer,     nullable=False)
    total_kendaraan   = db.Column(db.Integer,     nullable=False)

    # Label hasil prediksi model (Rendah / Sedang / Tinggi)
    tingkat_kepadatan = db.Column(db.String(10),  nullable=True)

    # Status validasi Human-in-the-Loop
    # pending   = belum divalidasi pakar
    # validated = pakar setuju dengan prediksi model
    # corrected = pakar mengkoreksi label
    status_validasi   = db.Column(db.String(15),  default='pending', nullable=False)

    # Label akhir setelah validasi pakar (bisa beda dari prediksi model)
    label_final       = db.Column(db.String(10),  nullable=True)

    # Nama file CSV asal data ini diupload
    nama_file         = db.Column(db.String(200), nullable=True)

    # ── KOLOM TAMBAHAN (sesuai permintaan) ──

    # Siapa yang menjalankan klasifikasi (upload CSV di halaman classifier)
    classified_by     = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )

    # Siapa yang melakukan validasi di halaman validasi
    validated_by      = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )

    # Timestamp
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)
    validated_at      = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Dataset {self.hari} {self.jam}:{self.menit} → {self.tingkat_kepadatan}>'


# ============================================================
# TABEL 4: retrain_history
# Menyimpan riwayat setiap proses retrain model
# (sesuai proposal BAB 3.3.7 & 3.3.8)
# ============================================================
class RetrainHistory(db.Model):
    __tablename__ = 'retrain_history'

    id          = db.Column(db.Integer, primary_key=True)
    versi       = db.Column(db.String(20), nullable=False)      # cth: v1.0, v1.1
    algoritma   = db.Column(db.String(50), nullable=False)      # Random Forest / SVM
    tanggal     = db.Column(db.DateTime,   default=datetime.utcnow)
    n_train     = db.Column(db.Integer,    nullable=True)       # jumlah data latih
    n_test      = db.Column(db.Integer,    nullable=True)       # jumlah data uji
    accuracy    = db.Column(db.Float,      nullable=True)       # 0.0–1.0
    precision   = db.Column(db.Float,      nullable=True)
    recall      = db.Column(db.Float,      nullable=True)
    f1_score    = db.Column(db.Float,      nullable=True)
    split_ratio = db.Column(db.Float,      default=0.8)         # 0.8 = 80/20
    cv_fold     = db.Column(db.Integer,    default=5)
    # Path file model .pkl yang disimpan
    model_path  = db.Column(db.String(300), nullable=True)
    # Apakah ini model yang sedang aktif digunakan
    is_active   = db.Column(db.Boolean,    default=False)
    # Catatan / keterangan tambahan
    catatan     = db.Column(db.Text,       nullable=True)

    # ── KOLOM TAMBAHAN: siapa yang menjalankan retrain ──
    user_id     = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )

    def __repr__(self):
        return f'<RetrainHistory {self.versi} — {self.algoritma} — acc:{self.accuracy}>'
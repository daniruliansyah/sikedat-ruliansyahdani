# app.py
import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_required, current_user

from models import db, bcrypt, User, Role, Dataset, RetrainHistory
from auth import auth_bp

# ============================================================
# INISIALISASI APLIKASI
# ============================================================
app = Flask(__name__)

app.config['SECRET_KEY'] = 'sikedat-dishub-surabaya-2026-secret'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(BASE_DIR, 'sikedat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view            = 'auth.login'
login_manager.login_message         = 'Silakan login untuk mengakses halaman ini.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)


# ============================================================
# DECORATOR CUSTOM
# ============================================================

def full_access_required(f):
    """Hanya untuk user yang sudah login DAN role akses_penuh=True
    (admin atau analis). Kalau belum login → ke halaman login.
    Kalau login tapi role tidak cukup → 403."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Silakan login untuk mengakses halaman ini.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.has_full_access:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Hanya untuk user dengan role admin (role_id=1 / nama='admin').
    Digunakan untuk halaman manajemen user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Silakan login untuk mengakses halaman ini.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.role or current_user.role.nama != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def login_required_only(f):
    """Hanya butuh sudah login, tidak peduli role-nya.
    Digunakan untuk halaman dashboard yang bisa diakses semua user Dishub."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Silakan login untuk mengakses halaman ini.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# INISIALISASI DATABASE + DATA AWAL
# ============================================================
def init_db():
    db.create_all()

    if not Role.query.first():
        roles = [
            Role(nama='admin',  deskripsi='Administrator — akses penuh ke semua fitur', akses_penuh=True),
            Role(nama='analis', deskripsi='Analis Data — klasifikasi, validasi, retrain', akses_penuh=True),
            Role(nama='staff',  deskripsi='Staff Dishub — beranda, dashboard, prediksi', akses_penuh=False),
        ]
        db.session.add_all(roles)
        db.session.commit()
        print('[DB] Roles dibuat: admin, analis, staff')

    if not User.query.filter_by(username='admin').first():
        role_admin = Role.query.filter_by(nama='admin').first()
        admin = User(username='admin', nama_lengkap='Administrator SIKEDAT',
                     role_id=role_admin.id, is_active=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('[DB] User admin dibuat  → username: admin | password: admin123')

    if not User.query.filter_by(username='analis_dishub').first():
        role_analis = Role.query.filter_by(nama='analis').first()
        analis = User(username='analis_dishub', nama_lengkap='Analis Data Dishub',
                      role_id=role_analis.id, is_active=True)
        analis.set_password('analis123')
        db.session.add(analis)
        db.session.commit()
        print('[DB] User analis dibuat → username: analis_dishub | password: analis123')

    if not User.query.filter_by(username='staff_dishub').first():
        role_staff = Role.query.filter_by(nama='staff').first()
        staff = User(username='staff_dishub', nama_lengkap='Staff Dinas Perhubungan',
                     role_id=role_staff.id, is_active=True)
        staff.set_password('staff123')
        db.session.add(staff)
        db.session.commit()
        print('[DB] User staff dibuat  → username: staff_dishub | password: staff123')


# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


# ============================================================
# CONTEXT PROCESSOR — variabel global untuk semua template
# ============================================================
@app.context_processor
def inject_globals():
    return {'now': datetime.utcnow()}


# ============================================================
# ROUTE — BERANDA  (PUBLIC — tidak perlu login)
# Masyarakat umum bisa melihat beranda
# ============================================================
@app.route('/')
def index():
    komposisi_per_hari = {
        'senin':  [320, 115, 34, 21], 'selasa': [298, 108, 30, 18],
        'rabu':   [310, 112, 32, 20], 'kamis':  [305, 110, 31, 19],
        'jumat':  [340, 124, 38, 24], 'sabtu':  [265,  95, 26, 15],
        'minggu': [240,  88, 22, 12],
    }

    total_data          = Dataset.query.count()
    total_kendaraan_all = db.session.query(db.func.sum(Dataset.total_kendaraan)).scalar() or 0
    pending_validasi    = Dataset.query.filter_by(status_validasi='pending').count()
    total_motor         = db.session.query(db.func.sum(Dataset.motor)).scalar() or 0
    total_mobil         = db.session.query(db.func.sum(Dataset.mobil)).scalar() or 0
    total_bus           = db.session.query(db.func.sum(Dataset.bus)).scalar() or 0
    total_truk          = db.session.query(db.func.sum(Dataset.truk)).scalar() or 0
    count_rendah        = Dataset.query.filter_by(tingkat_kepadatan='Rendah').count()
    count_sedang        = Dataset.query.filter_by(tingkat_kepadatan='Sedang').count()
    count_tinggi        = Dataset.query.filter_by(tingkat_kepadatan='Tinggi').count()
    pct_rendah          = round(count_rendah / total_data * 100) if total_data else 0
    pct_sedang          = round(count_sedang / total_data * 100) if total_data else 0
    pct_tinggi          = round(count_tinggi / total_data * 100) if total_data else 0

    return render_template(
        'index.html',
        komposisi_per_hari  = komposisi_per_hari,
        total_data          = f'{total_data:,}',
        total_kendaraan_all = f'{total_kendaraan_all:,}',
        total_motor         = f'{total_motor:,}',
        total_mobil         = f'{total_mobil:,}',
        total_bus           = f'{total_bus:,}',
        total_truk          = f'{total_truk:,}',
        pending_validasi    = pending_validasi,
        count_rendah        = count_rendah,
        count_sedang        = count_sedang,
        count_tinggi        = count_tinggi,
        pct_rendah          = pct_rendah,
        pct_sedang          = pct_sedang,
        pct_tinggi          = pct_tinggi,
    )


# ============================================================
# ROUTE — PREDIKSI  (PUBLIC — tidak perlu login)
# Masyarakat umum bisa mencoba prediksi
# ============================================================
@app.route('/prediksi', methods=['GET', 'POST'])
def prediksi():
    return render_template('prediksi.html')


# ============================================================
# ROUTE — DASHBOARD  (login wajib, semua role)
# ============================================================
@app.route('/dashboard')
@login_required_only
def dashboard():
    return render_template('dashboard.html')


# ============================================================
# ROUTE — CLASSIFIER  (login + akses_penuh)
# ============================================================
@app.route('/classifier', methods=['GET', 'POST'])
@full_access_required
def classifier():
    return render_template('classifier.html', step=1)

@app.route('/classifier/run', methods=['POST'])
@full_access_required
def run_classification():
    return redirect(url_for('classifier'))

@app.route('/classifier/download')
@full_access_required
def download_result():
    return redirect(url_for('classifier'))


# ============================================================
# ROUTE — VALIDASI  (login + akses_penuh)
# ============================================================
@app.route('/validasi')
@full_access_required
def validasi():
    data_pending = Dataset.query.filter_by(status_validasi='pending').all()
    total_data   = Dataset.query.count()
    validated    = Dataset.query.filter(Dataset.status_validasi.in_(['validated','corrected'])).count()
    pending      = Dataset.query.filter_by(status_validasi='pending').count()
    corrected    = Dataset.query.filter_by(status_validasi='corrected').count()
    return render_template('validasi.html',
        validation_data=data_pending, total_data=total_data,
        validated=validated, pending=pending, corrected=corrected)

@app.route('/validasi/save', methods=['GET', 'POST'])
@full_access_required
def save_validated():
    flash('Validasi berhasil disimpan.', 'success')
    return redirect(url_for('validasi'))


# ============================================================
# ROUTE — RETRAIN  (login + akses_penuh)
# ============================================================
@app.route('/retrain', methods=['GET', 'POST'])
@full_access_required
def retrain_model():
    model_aktif = RetrainHistory.query.filter_by(is_active=True).first()
    if model_aktif:
        model_info = {
            'algoritma' : model_aktif.algoritma,
            'versi'     : model_aktif.versi,
            'tanggal'   : model_aktif.tanggal.strftime('%d %b %Y, %H:%M') if model_aktif.tanggal else '—',
            'n_train'   : f'{model_aktif.n_train:,}' if model_aktif.n_train else '—',
            'accuracy'  : f'{model_aktif.accuracy*100:.2f}%' if model_aktif.accuracy else '—',
            'precision' : f'{model_aktif.precision*100:.2f}%' if model_aktif.precision else '—',
            'recall'    : f'{model_aktif.recall*100:.2f}%' if model_aktif.recall else '—',
            'f1'        : f'{model_aktif.f1_score*100:.2f}%' if model_aktif.f1_score else '—',
        }
    else:
        model_info = {k:'—' for k in ['algoritma','versi','tanggal','n_train','accuracy','precision','recall','f1']}

    retrain_history = RetrainHistory.query.order_by(RetrainHistory.tanggal.desc()).all()
    n_validated     = Dataset.query.filter(Dataset.status_validasi.in_(['validated','corrected'])).count()
    total_dataset   = Dataset.query.count()

    return render_template('retrain_model.html',
        model_info=model_info, retrain_history=retrain_history,
        n_validated=n_validated, total_dataset=f'{total_dataset:,}')

@app.route('/retrain/activate/<version>')
@full_access_required
def activate_model(version):
    RetrainHistory.query.update({'is_active': False})
    model = RetrainHistory.query.filter_by(versi=version).first()
    if model:
        model.is_active = True
        db.session.commit()
        flash(f'Model versi {version} berhasil diaktifkan.', 'success')
    return redirect(url_for('retrain_model'))


# ============================================================
# ROUTE — MANAJEMEN USER  (hanya admin)
# ============================================================

@app.route('/users')
@admin_required
def users_list():
    """Daftar semua user."""
    semua_user = User.query.order_by(User.id).all()
    semua_role = Role.query.all()
    return render_template('users.html',
        semua_user=semua_user, semua_role=semua_role, mode='list')


@app.route('/users/create', methods=['GET', 'POST'])
@admin_required
def users_create():
    """Form tambah user baru."""
    semua_role = Role.query.all()

    if request.method == 'POST':
        username     = request.form.get('username', '').strip()
        nama_lengkap = request.form.get('nama_lengkap', '').strip()
        password     = request.form.get('password', '')
        role_id      = request.form.get('role_id', type=int)

        # Validasi
        if not username or not password or not role_id:
            flash('Username, password, dan role wajib diisi.', 'danger')
            return render_template('users.html', semua_role=semua_role, mode='create')

        if User.query.filter_by(username=username).first():
            flash(f'Username "{username}" sudah digunakan.', 'danger')
            return render_template('users.html', semua_role=semua_role, mode='create')

        user = User(username=username, nama_lengkap=nama_lengkap,
                    role_id=role_id, is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'User "{username}" berhasil dibuat.', 'success')
        return redirect(url_for('users_list'))

    return render_template('users.html', semua_role=semua_role, mode='create')


@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def users_edit(user_id):
    """Form edit user."""
    user       = User.query.get_or_404(user_id)
    semua_role = Role.query.all()

    if request.method == 'POST':
        user.nama_lengkap = request.form.get('nama_lengkap', '').strip()

        # role_id: field di-disabled saat edit akun sendiri,
        # sehingga tidak ikut terkirim → pertahankan nilai lama
        role_id_baru = request.form.get('role_id', type=int)
        if role_id_baru is not None:
            user.role_id = role_id_baru
        # else: biarkan role_id tetap seperti semula

        # is_active: field di-disabled saat edit akun sendiri → pertahankan
        if user.id != current_user.id:
            user.is_active = 'is_active' in request.form
        # else: admin tidak bisa nonaktifkan diri sendiri, biarkan tetap aktif

        # Ganti password hanya jika field diisi
        new_password = request.form.get('password', '').strip()
        if new_password:
            if len(new_password) < 6:
                flash('Password minimal 6 karakter.', 'danger')
                semua_role = Role.query.all()
                return render_template('users.html', semua_role=semua_role,
                                       mode='edit', user=user)
            user.set_password(new_password)

        db.session.commit()
        flash(f'User "{user.username}" berhasil diperbarui.', 'success')
        return redirect(url_for('users_list'))

    return render_template('users.html', semua_role=semua_role,
                           mode='edit', user=user)


@app.route('/users/toggle/<int:user_id>', methods=['POST'])
@admin_required
def users_toggle(user_id):
    """Aktifkan / nonaktifkan user (soft delete)."""
    user = User.query.get_or_404(user_id)

    # Admin tidak bisa menonaktifkan dirinya sendiri
    if user.id == current_user.id:
        flash('Tidak dapat menonaktifkan akun Anda sendiri.', 'danger')
        return redirect(url_for('users_list'))

    user.is_active = not user.is_active
    db.session.commit()
    status = 'diaktifkan' if user.is_active else 'dinonaktifkan'
    flash(f'User "{user.username}" berhasil {status}.', 'success')
    return redirect(url_for('users_list'))


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
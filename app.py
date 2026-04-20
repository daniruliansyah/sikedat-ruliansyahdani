# app.py
import os, io, json
from datetime import datetime
from functools import wraps

import pandas as pd
from flask import (Flask, render_template, redirect, url_for,
                   request, flash, abort, send_file, session)
from flask_login import LoginManager, login_required, current_user

from models import db, bcrypt, User, Role, Dataset, RetrainHistory
from auth import auth_bp
import ml_utils

# ============================================================
# INISIALISASI
# ============================================================
app = Flask(__name__)
app.config['SECRET_KEY']                  = 'sikedat-dishub-surabaya-2026-secret'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']     = 'sqlite:///' + os.path.join(BASE_DIR, 'sikedat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER']               = os.path.join(BASE_DIR, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view             = 'auth.login'
login_manager.login_message          = 'Silakan login untuk mengakses halaman ini.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)

# ============================================================
# DECORATOR
# ============================================================
def full_access_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.has_full_access:
            abort(403)
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not (current_user.role and current_user.role.nama == 'admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated

def login_required_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# ============================================================
# INIT DB
# ============================================================
def init_db():
    db.create_all()
    if not Role.query.first():
        db.session.add_all([
            Role(nama='admin',  deskripsi='Administrator',   akses_penuh=True),
            Role(nama='analis', deskripsi='Analis Data',     akses_penuh=True),
            Role(nama='staff',  deskripsi='Staff Dishub',    akses_penuh=False),
        ])
        db.session.commit()
        print('[DB] Roles dibuat.')

    for uname, nama, role_nama, pwd in [
        ('admin',        'Administrator SIKEDAT',    'admin',  'admin123'),
        ('analis_dishub','Analis Data Dishub',        'analis', 'analis123'),
        ('staff_dishub', 'Staff Dinas Perhubungan',   'staff',  'staff123'),
    ]:
        if not User.query.filter_by(username=uname).first():
            r = Role.query.filter_by(nama=role_nama).first()
            u = User(username=uname, nama_lengkap=nama, role_id=r.id, is_active=True)
            u.set_password(pwd)
            db.session.add(u)
            db.session.commit()
            print(f'[DB] User dibuat: {uname} / {pwd}')

# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(403)
def forbidden(e):      return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):      return render_template('404.html'), 404

# ============================================================
# CONTEXT PROCESSOR
# ============================================================
@app.context_processor
def inject_globals():
    return {'now': datetime.utcnow()}

# ──────────────────────────────────────────────────────────────
#  HELPER — statistik dasar dari tabel dataset
# ──────────────────────────────────────────────────────────────
def get_stats():
    total_data          = Dataset.query.count()
    total_kendaraan_all = db.session.query(db.func.sum(Dataset.total_kendaraan)).scalar() or 0
    total_motor         = db.session.query(db.func.sum(Dataset.motor)).scalar() or 0
    total_mobil         = db.session.query(db.func.sum(Dataset.mobil)).scalar() or 0
    total_bus           = db.session.query(db.func.sum(Dataset.bus)).scalar() or 0
    total_truk          = db.session.query(db.func.sum(Dataset.truk)).scalar() or 0
    pending_validasi    = Dataset.query.filter_by(status_validasi='pending').count()
    count_rendah        = Dataset.query.filter_by(tingkat_kepadatan='Rendah').count()
    count_sedang        = Dataset.query.filter_by(tingkat_kepadatan='Sedang').count()
    count_tinggi        = Dataset.query.filter_by(tingkat_kepadatan='Tinggi').count()
    pct_rendah = round(count_rendah / total_data * 100) if total_data else 0
    pct_sedang = round(count_sedang / total_data * 100) if total_data else 0
    pct_tinggi = round(count_tinggi / total_data * 100) if total_data else 0
    return dict(
        total_data          = f'{total_data:,}',
        total_data_int      = total_data,
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


# ──────────────────────────────────────────────────────────────
#  HELPER — data untuk halaman Beranda (index.html)
# ──────────────────────────────────────────────────────────────
def get_index_data():
    """Hitung komposisi kendaraan rata-rata per hari dari DB."""
    import statistics

    HARI_MAP = {
        'Senin':1,'Selasa':2,'Rabu':3,
        'Kamis':4,'Jumat':5,'Sabtu':6,'Minggu':7
    }
    HARI_KEY = {
        'Senin':'senin','Selasa':'selasa','Rabu':'rabu',
        'Kamis':'kamis','Jumat':'jumat','Sabtu':'sabtu','Minggu':'minggu'
    }

    # Ambil semua data dari DB
    rows = Dataset.query.with_entities(
        Dataset.hari, Dataset.motor, Dataset.mobil,
        Dataset.bus,  Dataset.truk
    ).all()

    if not rows:
        # Kembalikan data kosong
        zero4 = [0, 0, 0, 0]
        return {
            'komposisi_per_hari': {h: zero4 for h in HARI_KEY.values()},
            'avg_motor': 0, 'avg_mobil': 0, 'avg_bus': 0, 'avg_truk': 0,
            'avg_motor_pct': 0, 'avg_mobil_pct': 0,
            'avg_bus_pct': 0,   'avg_truk_pct': 0,
            'last_file_name': None, 'last_file_rows': 0,
            'last_chart_labels': [], 'last_chart_data': [],
        }

    # Kelompokkan per hari
    from collections import defaultdict
    hari_data = defaultdict(lambda: {'motor':[],'mobil':[],'bus':[],'truk':[]})
    for r in rows:
        hari_data[r.hari]['motor'].append(r.motor)
        hari_data[r.hari]['mobil'].append(r.mobil)
        hari_data[r.hari]['bus'].append(r.bus)
        hari_data[r.hari]['truk'].append(r.truk)

    def avg(lst): return round(sum(lst)/len(lst), 1) if lst else 0

    komposisi_per_hari = {}
    for hari_id, key in HARI_KEY.items():
        d = hari_data.get(hari_id, {'motor':[0],'mobil':[0],'bus':[0],'truk':[0]})
        komposisi_per_hari[key] = [
            avg(d['motor']), avg(d['mobil']), avg(d['bus']), avg(d['truk'])
        ]

    # Rata-rata semua hari
    all_motor = [r.motor for r in rows]
    all_mobil = [r.mobil for r in rows]
    all_bus   = [r.bus   for r in rows]
    all_truk  = [r.truk  for r in rows]
    a_motor = avg(all_motor)
    a_mobil = avg(all_mobil)
    a_bus   = avg(all_bus)
    a_truk  = avg(all_truk)
    total_avg = a_motor + a_mobil + a_bus + a_truk or 1

    # Data file terakhir diproses (batch_id terbaru)
    last_batch = db.session.query(Dataset.batch_id, Dataset.nama_file).filter(
        Dataset.batch_id.isnot(None)
    ).order_by(Dataset.created_at.desc()).first()

    last_file_name  = last_batch.nama_file if last_batch else None
    last_chart_labels = []
    last_chart_data   = []

    if last_batch and last_batch.batch_id:
        batch_rows = Dataset.query.filter_by(
            batch_id=last_batch.batch_id
        ).order_by(Dataset.jam, Dataset.menit).all()

        last_file_rows = len(batch_rows)
        for br in batch_rows:
            last_chart_labels.append(f'{br.jam:02d}:{br.menit:02d}')
            last_chart_data.append(br.total_kendaraan)
    else:
        last_file_rows = 0

    return {
        'komposisi_per_hari' : komposisi_per_hari,
        'avg_motor'          : a_motor,
        'avg_mobil'          : a_mobil,
        'avg_bus'            : a_bus,
        'avg_truk'           : a_truk,
        'avg_motor_pct'      : round(a_motor / total_avg * 100),
        'avg_mobil_pct'      : round(a_mobil / total_avg * 100),
        'avg_bus_pct'        : round(a_bus   / total_avg * 100),
        'avg_truk_pct'       : round(a_truk  / total_avg * 100),
        'last_file_name'     : last_file_name,
        'last_file_rows'     : last_file_rows,
        'last_chart_labels'  : last_chart_labels,
        'last_chart_data'    : last_chart_data,
    }


# ──────────────────────────────────────────────────────────────
#  HELPER — data untuk halaman Dashboard (dashboard.html)
# ──────────────────────────────────────────────────────────────
def get_dashboard_data(filter_day='', filter_kategori=''):
    """Hitung semua agregasi dari DB untuk dashboard analitik.
    filter_day      : nama hari (Senin, Selasa, ...) atau kosong = semua
    filter_kategori : Rendah/Sedang/Tinggi atau kosong = semua
    """
    from collections import defaultdict

    query = Dataset.query
    if filter_day:
        query = query.filter(Dataset.hari == filter_day)
    if filter_kategori:
        label = filter_kategori.capitalize()
        query = query.filter(Dataset.tingkat_kepadatan == label)
    rows = query.all()
    if not rows:
        jam_zero = [0]*8
        return dict(
            avg_per_jam=[0]*8, max_per_jam=[0]*8,
            weekday_avg=jam_zero, weekend_avg=jam_zero,
            motor_per_jam=jam_zero, mobil_per_jam=jam_zero,
            bus_per_jam=jam_zero,   truk_per_jam=jam_zero,
            heavy_pct=0, avg_bus=0, avg_truk=0, total_heavy=0,
            heatmap_data={}, top_volume=[],
        )

    JAM_LIST = [6,7,8,15,16,17,18,19]
    WEEKEND  = {'Sabtu', 'Minggu'}

    # Kelompokkan per jam
    by_jam      = defaultdict(list)
    by_jam_wd   = defaultdict(list)  # weekday
    by_jam_we   = defaultdict(list)  # weekend
    by_jam_motor= defaultdict(list)
    by_jam_mobil= defaultdict(list)
    by_jam_bus  = defaultdict(list)
    by_jam_truk = defaultdict(list)
    by_hari_jam = defaultdict(list)  # untuk heatmap

    for r in rows:
        by_jam[r.jam].append(r.total_kendaraan)
        by_jam_motor[r.jam].append(r.motor)
        by_jam_mobil[r.jam].append(r.mobil)
        by_jam_bus[r.jam].append(r.bus)
        by_jam_truk[r.jam].append(r.truk)
        if r.hari in WEEKEND:
            by_jam_we[r.jam].append(r.total_kendaraan)
        else:
            by_jam_wd[r.jam].append(r.total_kendaraan)
        key = f'{r.hari}_{r.jam:02d}'
        by_hari_jam[key].append(r.total_kendaraan)

    def avg(lst): return round(sum(lst)/len(lst), 1) if lst else 0
    def mx(lst):  return max(lst) if lst else 0

    avg_per_jam   = [avg(by_jam[j])       for j in JAM_LIST]
    max_per_jam   = [mx(by_jam[j])        for j in JAM_LIST]
    weekday_avg   = [avg(by_jam_wd[j])    for j in JAM_LIST]
    weekend_avg   = [avg(by_jam_we[j])    for j in JAM_LIST]
    motor_per_jam = [avg(by_jam_motor[j]) for j in JAM_LIST]
    mobil_per_jam = [avg(by_jam_mobil[j]) for j in JAM_LIST]
    bus_per_jam   = [avg(by_jam_bus[j])   for j in JAM_LIST]
    truk_per_jam  = [avg(by_jam_truk[j])  for j in JAM_LIST]

    # Kendaraan berat
    all_bus   = sum(r.bus  for r in rows)
    all_truk  = sum(r.truk for r in rows)
    all_total = sum(r.total_kendaraan for r in rows) or 1
    heavy_pct = round((all_bus + all_truk) / all_total * 100, 1)
    total_heavy = all_bus + all_truk

    # Heatmap: {'Senin_06': avg_total, ...}
    heatmap_data = {}
    HARI_LIST = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
    for hari in HARI_LIST:
        for jam in JAM_LIST:
            key = f'{hari}_{jam:02d}'
            vals = by_hari_jam.get(key, [])
            heatmap_data[key] = round(avg(vals)) if vals else None

    # Top 10 interval volume tertinggi
    top_rows = sorted(rows, key=lambda r: r.total_kendaraan, reverse=True)[:10]
    top_volume = [{
        'hari'    : r.hari,
        'jam'     : r.jam,
        'menit'   : r.menit,
        'motor'   : r.motor,
        'mobil'   : r.mobil,
        'bus'     : r.bus,
        'truk'    : r.truk,
        'total'   : r.total_kendaraan,
        'kategori': (r.tingkat_kepadatan or '').lower(),
    } for r in top_rows]

    return dict(
        avg_per_jam   = avg_per_jam,
        max_per_jam   = max_per_jam,
        weekday_avg   = weekday_avg,
        weekend_avg   = weekend_avg,
        motor_per_jam = motor_per_jam,
        mobil_per_jam = mobil_per_jam,
        bus_per_jam   = bus_per_jam,
        truk_per_jam  = truk_per_jam,
        heavy_pct     = heavy_pct,
        avg_bus       = round(avg([r.bus  for r in rows]), 1),
        avg_truk      = round(avg([r.truk for r in rows]), 1),
        total_heavy   = f'{total_heavy:,}',
        heatmap_data  = heatmap_data,
        top_volume    = top_volume,
    )

# ============================================================
# ROUTE — BERANDA  (public)
# ============================================================
@app.route('/')
def index():
    stats  = get_stats()
    idata  = get_index_data()
    return render_template('index.html', **stats, **idata)

# ============================================================
# ROUTE — PREDIKSI  (public)
# ============================================================
@app.route('/prediksi', methods=['GET', 'POST'])
def prediksi():
    prediction = None
    form_data  = None

    if request.method == 'POST':
        hari          = request.form.get('hari', '')
        sesi          = request.form.get('sesi', '')
        jam           = request.form.get('jam', '')
        menit_raw     = request.form.get('menit', '')
        menit_rounded = request.form.get('menit_rounded', menit_raw)

        form_data = {'hari': hari, 'sesi': sesi, 'jam': jam, 'menit': menit_raw}

        if not all([hari, jam, menit_rounded]):
            flash('Lengkapi semua field sebelum prediksi.', 'danger')
        else:
            try:
                prediction = ml_utils.predict_single(
                    hari=hari, jam=int(jam), menit=int(menit_rounded)
                )
            except FileNotFoundError:
                flash('Model belum tersedia. Jalankan train_models.py terlebih dahulu.', 'danger')
            except Exception as e:
                flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    return render_template('prediksi.html',
                           prediction=prediction, form_data=form_data)

# ============================================================
# ROUTE — DASHBOARD  (login semua role)
# ============================================================
@app.route('/dashboard')
@login_required_only
def dashboard():
    # Ambil filter dari query string (?filter_day=Senin&filter_kategori=tinggi)
    filter_day      = request.args.get('filter_day', '').strip()
    filter_kategori = request.args.get('filter_kategori', '').strip()

    stats = get_stats()
    ddata = get_dashboard_data(filter_day=filter_day, filter_kategori=filter_kategori)
    return render_template('dashboard.html',
        filter_day      = filter_day,
        filter_kategori = filter_kategori,
        **stats, **ddata)

# ============================================================
# ROUTE — CLASSIFIER  (full_access)
# ============================================================
@app.route('/classifier', methods=['GET', 'POST'])
@full_access_required
def classifier():
    if request.method == 'POST':
        # ── Step 1: Terima file CSV
        file = request.files.get('csv_file')
        if not file or file.filename == '':
            flash('Pilih file CSV terlebih dahulu.', 'danger')
            return render_template('classifier.html', step=1)

        if not file.filename.endswith('.csv'):
            flash('File harus berformat .csv', 'danger')
            return render_template('classifier.html', step=1)

        # Baca CSV
        try:
            df = pd.read_csv(file)
        except Exception as e:
            flash(f'Gagal membaca file CSV: {str(e)}', 'danger')
            return render_template('classifier.html', step=1)

        # Validasi kolom
        required = ['hari','jam','menit','motor','mobil','bus','truk','total_kendaraan']
        missing  = [c for c in required if c not in df.columns]
        if missing:
            flash(f'Kolom tidak ditemukan: {", ".join(missing)}', 'danger')
            return render_template('classifier.html', step=1)

        # Simpan ke FILE di disk (session terlalu kecil untuk CSV besar ~4KB limit)
        import uuid
        tmp_name = f"upload_{uuid.uuid4().hex}.csv"
        tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], tmp_name)
        df.to_csv(tmp_path, index=False)

        # Ambil tanggal rekaman dari form (opsional)
        tanggal_rekaman = request.form.get('tanggal_rekaman', '').strip()

        # Session hanya menyimpan PATH file + info kecil (aman)
        session['classifier_tmp']      = tmp_path
        session['classifier_filename'] = file.filename
        session['classifier_tanggal']  = tanggal_rekaman

        preview_data = df.to_dict('records')  # tampilkan semua baris
        return render_template('classifier.html', step=2,
            preview_data    = preview_data,
            preview_rows    = len(df),
            file_path       = tmp_path,
            tanggal_rekaman = tanggal_rekaman)

    return render_template('classifier.html', step=1)


@app.route('/classifier/run', methods=['POST'])
@full_access_required
def run_classification():
    # Ambil path file dari session (bukan data CSV langsung)
    tmp_path = session.get('classifier_tmp')
    if not tmp_path or not os.path.exists(tmp_path):
        flash('File tidak ditemukan. Silakan upload ulang file CSV.', 'warning')
        return redirect(url_for('classifier'))

    df = pd.read_csv(tmp_path)

    try:
        df_result = ml_utils.classify_dataframe(df)
    except FileNotFoundError:
        flash('Model belum tersedia. Jalankan train_models.py terlebih dahulu.', 'danger')
        return redirect(url_for('classifier'))
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('classifier'))

    # Simpan hasil ke FILE di disk juga
    import uuid
    batch_id    = uuid.uuid4().hex          # ID unik untuk batch ini
    result_name = f"result_{batch_id}.csv"
    result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_name)
    df_result.to_csv(result_path, index=False)

    session['classification_result_path'] = result_path
    session['classification_filename']    = session.get('classifier_filename', 'data.csv')
    session['classification_batch_id']    = batch_id
    session['classification_tanggal']     = session.get('classifier_tanggal', '')

    count_rendah = int((df_result['tingkat_kepadatan'] == 'Rendah').sum())
    count_sedang = int((df_result['tingkat_kepadatan'] == 'Sedang').sum())
    count_tinggi = int((df_result['tingkat_kepadatan'] == 'Tinggi').sum())

    result_data = df_result.to_dict('records')

    return render_template('classifier.html', step=4,
        result_data   = result_data,
        count_rendah  = count_rendah,
        count_sedang  = count_sedang,
        count_tinggi  = count_tinggi,
        model_used    = ml_utils.load_metadata().get('best_algo', 'Model'),
    )


@app.route('/classifier/download')
@full_access_required
def download_result():
    result_path = session.get('classification_result_path')
    if not result_path or not os.path.exists(result_path):
        flash('Tidak ada hasil untuk didownload. Upload dan klasifikasi ulang.', 'warning')
        return redirect(url_for('classifier'))

    df = pd.read_csv(result_path)
    # Hanya kolom utama yang didownload
    cols = ['hari','jam','menit','motor','mobil','bus','truk',
            'total_kendaraan','tingkat_kepadatan','confidence']
    cols = [c for c in cols if c in df.columns]
    buf  = io.BytesIO()
    df[cols].to_csv(buf, index=False)
    buf.seek(0)
    filename = 'hasil_klasifikasi_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
    return send_file(buf, mimetype='text/csv',
                     as_attachment=True, download_name=filename)


# ============================================================
# ROUTE — VALIDASI  (full_access)
# Data dari session classifier ATAU dari database (pending)
# ============================================================
@app.route('/validasi')
@full_access_required
def validasi():
    # ── SISTEM ANTRIAN: ambil batch_id tertua yang masih ada data pending ──
    from sqlalchemy import func

    # Subquery: batch_id tertua berdasarkan created_at minimum
    oldest_subq = db.session.query(
        Dataset.batch_id,
        func.min(Dataset.created_at).label('min_created')
    ).filter(
        Dataset.status_validasi == 'pending',
        Dataset.batch_id.isnot(None)
    ).group_by(Dataset.batch_id).order_by('min_created').first()

    current_batch_id = oldest_subq[0] if oldest_subq else None

    # Tampilkan hanya batch tertua
    if current_batch_id:
        batch_data = Dataset.query.filter_by(
            status_validasi='pending', batch_id=current_batch_id
        ).order_by(Dataset.id.asc()).all()
    else:
        # Fallback: data pending tanpa batch_id
        batch_data = Dataset.query.filter_by(
            status_validasi='pending'
        ).order_by(Dataset.id.asc()).all()

    # Hitung semua batch yang masih pending (untuk info antrian)
    semua_batch_pending = db.session.query(
        Dataset.batch_id,
        func.count(Dataset.id).label('jumlah'),
        func.min(Dataset.created_at).label('dibuat'),
        func.min(Dataset.nama_file).label('nama_file')
    ).filter(
        Dataset.status_validasi == 'pending',
        Dataset.batch_id.isnot(None)
    ).group_by(Dataset.batch_id).order_by('dibuat').all()

    antrian_info = [{
        'batch_id'  : b.batch_id,
        'jumlah'    : b.jumlah,
        'dibuat'    : b.dibuat,
        'nama_file' : b.nama_file,
        'is_current': b.batch_id == current_batch_id,
    } for b in semua_batch_pending]

    # Statistik
    total_data    = Dataset.query.count()
    validated     = Dataset.query.filter(
        Dataset.status_validasi.in_(['validated','corrected'])
    ).count()
    pending_total = Dataset.query.filter_by(status_validasi='pending').count()
    corrected     = Dataset.query.filter_by(status_validasi='corrected').count()

    return render_template('validasi.html',
        validation_data  = batch_data,
        total_data       = len(batch_data),
        validated        = validated,
        pending          = len(batch_data),
        corrected        = corrected,
        current_batch_id = current_batch_id,
        antrian_info     = antrian_info,
        antrian_count    = len(antrian_info),
        global_total     = total_data,
        global_pending   = pending_total,
    )


@app.route('/validasi/save', methods=['POST'])
@full_access_required
def save_validated():
    """
    Terima POST berisi:
    - changes: JSON array [{id, label}] — semua baris yang ada di halaman
    - selected_ids: JSON array [id, id, ...] — hanya baris yang di-checklist

    Jika selected_ids kosong → validasi semua baris yang dikirim.
    Jika selected_ids ada    → hanya validasi baris yang dipilih.
    """
    changes_json  = request.form.get('changes', '[]')
    selected_json = request.form.get('selected_ids', '[]')

    try:
        changes      = json.loads(changes_json)
        selected_ids = set(json.loads(selected_json))
    except json.JSONDecodeError:
        flash('Data validasi tidak valid.', 'danger')
        return redirect(url_for('validasi'))

    # Jika ada pilihan spesifik → filter hanya baris yang dipilih
    if selected_ids:
        changes = [c for c in changes if c.get('id') in selected_ids]

    if not changes:
        flash('Tidak ada baris yang dipilih untuk divalidasi.', 'warning')
        return redirect(url_for('validasi'))

    updated = 0
    for change in changes:
        row = Dataset.query.get(change.get('id'))
        if not row:
            continue
        new_label = change.get('label', '').capitalize()
        if new_label not in ['Rendah', 'Sedang', 'Tinggi']:
            continue

        # Cek apakah validator mengoreksi label prediksi model
        is_corrected = (new_label != row.tingkat_kepadatan)

        row.status_validasi   = 'corrected' if is_corrected else 'validated'
        row.label_final       = new_label
        # Update tingkat_kepadatan = label_final yang sudah diverifikasi pakar
        # → agar saat retrain, semua data konsisten pakai kolom tingkat_kepadatan
        row.tingkat_kepadatan = new_label
        row.validated_by      = current_user.id
        row.validated_at      = datetime.utcnow()
        updated += 1

    db.session.commit()

    # Setelah semua batch selesai, cek apakah ada batch berikutnya
    sisa_pending = Dataset.query.filter_by(
        status_validasi='pending', batch_id=changes[0].get('batch_id') if changes else None
    ).count() if changes else 0

    if sisa_pending == 0:
        next_batch = db.session.query(Dataset.batch_id).filter_by(
            status_validasi='pending'
        ).order_by(Dataset.created_at.asc()).first()
        if next_batch:
            flash(
                f'{updated} baris disimpan. '
                f'Batch berikutnya siap divalidasi.',
                'success'
            )
        else:
            flash(f'{updated} baris disimpan. Semua batch selesai divalidasi! ✅', 'success')
    else:
        flash(f'{updated} baris disimpan. Masih ada {sisa_pending} baris dalam batch ini.', 'success')

    return redirect(url_for('validasi'))


@app.route('/validasi/import', methods=['POST'])
@full_access_required
def import_classification_to_validasi():
    """
    Simpan hasil klasifikasi dari session ke tabel dataset
    dengan status 'pending' (belum divalidasi).
    Dipanggil dari halaman classifier step 4 → Validasi Hasil.
    """
    result_path = session.get('classification_result_path')
    file_name   = session.get('classification_filename', 'data.csv')

    if not result_path or not os.path.exists(result_path):
        flash('Tidak ada hasil klasifikasi. Upload dan klasifikasi ulang CSV.', 'warning')
        return redirect(url_for('classifier'))

    df = pd.read_csv(result_path)

    batch_id        = session.get('classification_batch_id', 'batch_unknown')
    tanggal_str     = session.get('classification_tanggal', '')
    tanggal_rekaman = None
    if tanggal_str:
        from datetime import date as date_type
        try:
            tanggal_rekaman = date_type.fromisoformat(tanggal_str)
        except ValueError:
            tanggal_rekaman = None

    inserted = 0
    for _, row in df.iterrows():
        new_row = Dataset(
            hari              = str(row['hari']),
            jam               = int(row['jam']),
            menit             = int(row['menit']),
            motor             = int(row['motor']),
            mobil             = int(row['mobil']),
            bus               = int(row['bus']),
            truk              = int(row['truk']),
            total_kendaraan   = int(row['total_kendaraan']),
            tingkat_kepadatan = str(row['tingkat_kepadatan']),
            label_final       = str(row['tingkat_kepadatan']),
            status_validasi   = 'pending',
            nama_file         = file_name,
            tanggal           = tanggal_rekaman,
            batch_id          = batch_id,
            classified_by     = current_user.id,
        )
        db.session.add(new_row)
        inserted += 1

    db.session.commit()

    # Hapus file sementara dari disk + bersihkan session
    for key in ['classification_result_path', 'classifier_tmp']:
        fpath = session.pop(key, None)
        if fpath and os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass
    for key in ['classifier_filename','classification_filename',
                'classification_batch_id','classification_tanggal','classifier_tanggal']:
        session.pop(key, None)

    flash(f'{inserted} baris berhasil dikirim ke antrian validasi.', 'success')
    return redirect(url_for('validasi'))


# ============================================================
# ROUTE — RETRAIN  (full_access)
# ============================================================
@app.route('/retrain', methods=['GET', 'POST'])
@full_access_required
def retrain_model():
    if request.method == 'POST':
        return _do_retrain()

    model_aktif     = RetrainHistory.query.filter_by(is_active=True).first()
    retrain_history = RetrainHistory.query.order_by(RetrainHistory.tanggal.desc()).all()
    n_validated     = Dataset.query.filter(Dataset.status_validasi.in_(['validated','corrected'])).count()
    n_new_data      = Dataset.query.filter_by(status_validasi='pending').count()
    total_dataset   = Dataset.query.count()

    def fmt_model(m):
        if not m: return {k:'—' for k in ['algoritma','versi','tanggal','n_train','accuracy','precision','recall','f1']}
        return {
            'algoritma': m.algoritma,
            'versi'    : m.versi,
            'tanggal'  : m.tanggal.strftime('%d %b %Y, %H:%M') if m.tanggal else '—',
            'n_train'  : f'{m.n_train:,}' if m.n_train else '—',
            'accuracy' : f'{m.accuracy*100:.2f}%' if m.accuracy else '—',
            'precision': f'{m.precision*100:.2f}%' if m.precision else '—',
            'recall'   : f'{m.recall*100:.2f}%'    if m.recall    else '—',
            'f1'       : f'{m.f1_score*100:.2f}%'  if m.f1_score  else '—',
        }

    return render_template('retrain_model.html',
        model_info      = fmt_model(model_aktif),
        retrain_history = retrain_history,
        n_validated     = n_validated,
        n_new_data      = n_new_data,
        total_dataset   = f'{total_dataset:,}',
    )


def _do_retrain():
    """Jalankan retrain model dari dataset yang sudah tervalidasi di DB."""
    import subprocess, sys
    split_ratio = float(request.form.get('split_ratio', 0.8))
    cv_fold     = int(request.form.get('cv_fold', 5))

    # Retrain menggunakan data yang sudah tervalidasi:
    # - 'validated' : label disetujui pakar (tidak dikoreksi)
    # - 'corrected' : label dikoreksi pakar
    # Keduanya dipakai karena sudah dikonfirmasi oleh manusia
    rows = Dataset.query.filter(
        Dataset.status_validasi.in_(['validated', 'corrected'])
    ).all()

    print(f'[RETRAIN] Total data validated+corrected: {len(rows)} baris')

    if len(rows) < 20:
        flash(
            f'Data tervalidasi (validated + corrected) terlalu sedikit ({len(rows)} baris). '
            f'Minimal 20 baris. Lakukan validasi data terlebih dahulu.',
            'danger'
        )
        return redirect(url_for('retrain_model'))

    # Ekspor ke CSV — pakai tingkat_kepadatan (sudah = label_final setelah validasi)
    df = pd.DataFrame([{
        'hari'             : r.hari,
        'jam'              : r.jam,
        'menit'            : r.menit,
        'motor'            : r.motor,
        'mobil'            : r.mobil,
        'bus'              : r.bus,
        'truk'             : r.truk,
        'total_kendaraan'  : r.total_kendaraan,
        'tingkat_kepadatan': r.tingkat_kepadatan,  # ← pakai ini, bukan label_final
    } for r in rows])

    tmp_csv = os.path.join(BASE_DIR, 'dataset_dummy_berlabel.csv')
    df.to_csv(tmp_csv, index=False)

    # Jalankan training
    result = subprocess.run(
        [sys.executable, 'train_models.py'],
        capture_output=True, text=True, cwd=BASE_DIR
    )

    if result.returncode != 0:
        flash(f'Retrain gagal: {result.stderr[:300]}', 'danger')
        return redirect(url_for('retrain_model'))

    # Baca metadata hasil training
    meta = ml_utils.load_metadata()
    algo = meta.get('best_algo', 'Random Forest')

    # Hitung versi berikutnya
    last = RetrainHistory.query.order_by(RetrainHistory.id.desc()).first()
    if last and last.versi.startswith('v'):
        try:
            num     = float(last.versi[1:]) + 0.1
            new_ver = f'v{num:.1f}'
        except ValueError:
            new_ver = 'v2.0'
    else:
        new_ver = 'v1.0'

    # Non-aktifkan semua, tambah record baru
    RetrainHistory.query.update({'is_active': False})
    chosen = meta.get(algo.lower().replace(' ','_'), meta.get('rf', {}))
    if algo == 'Random Forest': chosen = meta.get('rf', {})
    elif algo == 'SVM':         chosen = meta.get('svm', {})

    record = RetrainHistory(
        versi       = new_ver,
        algoritma   = algo,
        n_train     = meta.get('n_train'),
        n_test      = meta.get('n_test'),
        accuracy    = chosen.get('accuracy'),
        precision   = chosen.get('precision'),
        recall      = chosen.get('recall'),
        f1_score    = chosen.get('f1_score'),
        split_ratio = split_ratio,
        cv_fold     = cv_fold,
        model_path  = 'models/model_aktif.pkl',
        is_active   = True,
        user_id     = current_user.id,
        catatan     = f'Retrain dari {len(rows)} data tervalidasi.',
    )
    db.session.add(record)
    db.session.commit()

    flash(f'Retrain berhasil! Model {new_ver} ({algo}) — Akurasi: {chosen.get("accuracy",0)*100:.2f}%', 'success')
    return redirect(url_for('retrain_model'))


@app.route('/retrain/activate/<version>')
@full_access_required
def activate_model(version):
    RetrainHistory.query.update({'is_active': False})
    m = RetrainHistory.query.filter_by(versi=version).first()
    if m:
        m.is_active = True
        db.session.commit()
        flash(f'Model {version} diaktifkan.', 'success')
    return redirect(url_for('retrain_model'))


# ============================================================
# ROUTE — MANAJEMEN USER  (admin only)
# ============================================================
@app.route('/users')
@admin_required
def users_list():
    return render_template('users.html',
        semua_user=User.query.order_by(User.id).all(),
        semua_role=Role.query.all(), mode='list')

@app.route('/users/create', methods=['GET','POST'])
@admin_required
def users_create():
    semua_role = Role.query.all()
    if request.method == 'POST':
        username     = request.form.get('username','').strip()
        nama_lengkap = request.form.get('nama_lengkap','').strip()
        password     = request.form.get('password','')
        role_id      = request.form.get('role_id', type=int)
        if not username or not password or not role_id:
            flash('Username, password, dan role wajib diisi.', 'danger')
            return render_template('users.html', semua_role=semua_role, mode='create')
        if User.query.filter_by(username=username).first():
            flash(f'Username "{username}" sudah digunakan.', 'danger')
            return render_template('users.html', semua_role=semua_role, mode='create')
        u = User(username=username, nama_lengkap=nama_lengkap, role_id=role_id, is_active=True)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash(f'User "{username}" berhasil dibuat.', 'success')
        return redirect(url_for('users_list'))
    return render_template('users.html', semua_role=semua_role, mode='create')

@app.route('/users/edit/<int:user_id>', methods=['GET','POST'])
@admin_required
def users_edit(user_id):
    user       = User.query.get_or_404(user_id)
    semua_role = Role.query.all()
    if request.method == 'POST':
        user.nama_lengkap = request.form.get('nama_lengkap','').strip()
        role_id_baru = request.form.get('role_id', type=int)
        if role_id_baru is not None:
            user.role_id = role_id_baru
        if user.id != current_user.id:
            user.is_active = 'is_active' in request.form
        new_pwd = request.form.get('password','').strip()
        if new_pwd:
            if len(new_pwd) < 6:
                flash('Password minimal 6 karakter.', 'danger')
                return render_template('users.html', semua_role=semua_role, mode='edit', user=user)
            user.set_password(new_pwd)
        db.session.commit()
        flash(f'User "{user.username}" berhasil diperbarui.', 'success')
        return redirect(url_for('users_list'))
    return render_template('users.html', semua_role=semua_role, mode='edit', user=user)

@app.route('/users/toggle/<int:user_id>', methods=['POST'])
@admin_required
def users_toggle(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Tidak dapat menonaktifkan akun Anda sendiri.', 'danger')
        return redirect(url_for('users_list'))
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User "{user.username}" {"diaktifkan" if user.is_active else "dinonaktifkan"}.', 'success')
    return redirect(url_for('users_list'))


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
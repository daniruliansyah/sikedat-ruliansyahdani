# app.py
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

# ── Halaman Utama ──
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

# ── Classifier ──
@app.route('/classifier', methods=['GET', 'POST'])
def classifier():
    return render_template('classifier.html', step=1)

@app.route('/classifier/run', methods=['POST'])
def run_classification():
    # TODO: implementasi klasifikasi
    return redirect(url_for('classifier'))

@app.route('/classifier/download')
def download_result():
    # TODO: implementasi download
    return redirect(url_for('classifier'))

# ── Dashboard ──
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ── Prediksi ──
@app.route('/prediksi', methods=['GET', 'POST'])
def prediksi():
    return render_template('prediksi.html')

# ── Validasi ──
@app.route('/validasi')
def validasi():
    return render_template('validasi.html')

@app.route('/validasi/save')
def save_validated():
    # TODO: implementasi simpan validasi
    return redirect(url_for('validasi'))

# ── Retrain ──
@app.route('/retrain', methods=['GET', 'POST'])
def retrain_model():
    return render_template('retrain_model.html')

@app.route('/retrain/activate/<version>')
def activate_model(version):
    # TODO: implementasi aktivasi model
    return redirect(url_for('retrain_model'))

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def index():
    komposisi_per_hari = {
        'senin':  [320, 115, 34, 21],
        'selasa': [298, 108, 30, 18],
        'rabu':   [310, 112, 32, 20],
        'kamis':  [305, 110, 31, 19],
        'jumat':  [340, 124, 38, 24],
        'sabtu':  [265,  95, 26, 15],
        'minggu': [240,  88, 22, 12],
    }
    return render_template('index.html', komposisi_per_hari=komposisi_per_hari)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/classifier', methods=['GET', 'POST'])
def classifier():
    return render_template('classifier.html', step=1)

@app.route('/classifier/run', methods=['POST'])
def run_classification():
    return redirect(url_for('classifier'))

@app.route('/classifier/download')
def download_result():
    return redirect(url_for('classifier'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/prediksi', methods=['GET', 'POST'])
def prediksi():
    return render_template('prediksi.html')

@app.route('/validasi')
def validasi():
    return render_template('validasi.html')

@app.route('/validasi/save')
def save_validated():
    return redirect(url_for('validasi'))

@app.route('/retrain', methods=['GET', 'POST'])
def retrain_model():
    model_info = {
        'algoritma' : 'Random Forest',
        'versi'     : 'v1.0',
        'tanggal'   : '—',
        'n_train'   : '—',
        'accuracy'  : '—',
        'precision' : '—',
        'recall'    : '—',
        'f1'        : '—',
    }
    return render_template('retrain_model.html', model_info=model_info)

@app.route('/retrain/activate/<version>')
def activate_model(version):
    return redirect(url_for('retrain_model'))

if __name__ == '__main__':
    app.run(debug=True)
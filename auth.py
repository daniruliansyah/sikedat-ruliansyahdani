# auth.py
# Route untuk login dan logout

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Kalau sudah login, langsung ke beranda
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and user.is_active and user.check_password(password):
            login_user(user, remember='remember' in request.form)
            flash(f'Selamat datang, {user.nama_lengkap or user.username}!', 'success')
            # Redirect ke halaman yang diminta sebelumnya (kalau ada)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Username atau password salah. Silakan coba lagi.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil keluar dari sistem.', 'info')
    return redirect(url_for('index'))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from .models import get_user_by_username, create_user

auth_bp = Blueprint('auth', __name__)


class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get("username")
        self.username = user_data.get("username")
        self.email = user_data.get("email")
        self.full_name = user_data.get("full_name")


@login_manager.user_loader
def load_user(user_id):
    data = get_user_by_username(user_id)
    return User(data) if data else None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        if not username or not password:
            flash('Please enter both username and password')
            return render_template('login.html')

        user_data = get_user_by_username(username)
        if user_data and check_password_hash(user_data.get('password_hash', ''), password):
            login_user(User(user_data), remember=remember)
            return redirect(url_for('main.index'))

        flash('Invalid username or password')
        return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')

        if not username or not email or not password or not full_name:
            flash('All fields are required')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters')
            return render_template('register.html')

        if get_user_by_username(username):
            flash('Username already taken')
            return render_template('register.html')

        if create_user(username, email, generate_password_hash(password), full_name):
            flash('Registration successful! Please log in.')
            return redirect(url_for('auth.login'))

        flash('Registration failed. Please try again.')
        return render_template('register.html')

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

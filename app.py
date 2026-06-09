import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

from utils import calculate_nutrition
from gemini_utils import get_gemini_response
from database import init_db
from mongo_db import init_mongodb, save_user, get_user_by_email, create_user, get_user_by_username

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

init_db(app)
init_mongodb()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get("username")
        self.username = user_data.get("username")
        self.email = user_data.get("email")
        self.full_name = user_data.get("full_name")


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_username(user_id)
    if user_data:
        return User(user_data)
    return None


@app.route('/')
@login_required
def index():
    return render_template('index_extended.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        if not username or not password:
            flash('Please enter both username and password')
            return render_template('login.html')

        user_data = get_user_by_username(username)
        if user_data and check_password_hash(user_data.get('password_hash', ''), password):
            user = User(user_data)
            login_user(user, remember=remember)
            return redirect(url_for('index'))

        flash('Invalid username or password')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

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

        existing = get_user_by_username(username)
        if existing:
            flash('Username already taken')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        success = create_user(username, email, password_hash, full_name)

        if success:
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))

        flash('Registration failed. Please try again.')
        return render_template('register.html')

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        data = request.json

        height = float(data.get('height', 0))
        weight = float(data.get('weight', 0))
        age = int(data.get('age', 0))
        gender = data.get('gender', 'male')
        activity_level = data.get('activityLevel', 'sedentary')
        goal = data.get('goal', 'maintain')
        diet_type = data.get('dietType', 'balanced')
        metabolic_type = data.get('metabolicType', 'mixed')

        if height <= 0 or weight <= 0 or age <= 0:
            return jsonify({'error': 'Invalid input values'}), 400

        nutrition_data = calculate_nutrition(
            height, weight, age, gender,
            activity_level, goal, diet_type, metabolic_type
        )

        return jsonify(nutrition_data)

    except Exception as e:
        logging.error(f"Error calculating nutrition: {str(e)}")
        return jsonify({'error': 'Failed to calculate nutrition needs'}), 500


@app.route('/save-user', methods=['POST'])
@login_required
def save_user_profile():
    try:
        data = request.json

        user_data = {
            "full_name": data.get('fullName', ''),
            "email": data.get('email', ''),
            "age": int(data.get('age', 0)),
            "gender": data.get('gender', ''),
            "height": float(data.get('height', 0)),
            "weight": float(data.get('weight', 0)),
            "activity_level": data.get('activityLevel', ''),
            "dietary_preference": data.get('dietType', ''),
            "fitness_goal": data.get('goal', ''),
            "metabolism_type": data.get('metabolicType', ''),
            "location": data.get('location', ''),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        if not user_data["email"] or not user_data["full_name"]:
            return jsonify({'error': 'Email and full name are required'}), 400

        success = save_user(user_data)

        if success:
            return jsonify({
                'success': True,
                'message': 'User profile saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save user profile'
            }), 500

    except Exception as e:
        logging.error(f"Error saving user profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while saving your profile'
        }), 500


@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        nutrition_data = data.get('nutritionData', {})
        chat_history = data.get('chatHistory', [])

        response = get_gemini_response(message, nutrition_data, chat_history)

        return jsonify({'response': response})

    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'response': 'Sorry, I encountered an error processing your request. Please try again.'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

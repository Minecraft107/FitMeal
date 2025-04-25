import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from utils import calculate_nutrition
from gemini_utils import get_gemini_response
from database import init_db, db
from mongo_db import init_mongodb, save_user, get_user_by_email
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize databases
init_db(app)
init_mongodb()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Custom unauthorized handler for API requests
@login_manager.unauthorized_handler
def unauthorized_handler():
    if request.is_json or request.headers.get('Content-Type') == 'application/json':
        return jsonify({'error': 'Unauthorized access. Please log in.'}), 401
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID for Flask-Login."""
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Render the main page with the chat interface."""
    if current_user.is_authenticated:
        return render_template('index_extended.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        # Check if username or email already exists
        username_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        
        if username_exists:
            flash('Username already exists')
        elif email_exists:
            flash('Email already exists')
        else:
            # Create new user
            user = User(username=username, email=email, full_name=full_name)
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error registering user: {str(e)}")
                flash('An error occurred during registration')
                
    return render_template('register.html')

@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    """Calculate nutrition needs based on user data."""
    try:
        data = request.json
        
        # Extract user data
        height = float(data.get('height', 0))
        weight = float(data.get('weight', 0))
        age = int(data.get('age', 0))
        gender = data.get('gender', 'male')
        activity_level = data.get('activityLevel', 'sedentary')
        goal = data.get('goal', 'maintain')
        diet_type = data.get('dietType', 'balanced')
        metabolic_type = data.get('metabolicType', 'mixed')
        
        # Validate inputs
        if height <= 0 or weight <= 0 or age <= 0:
            return jsonify({'error': 'Invalid input values'}), 400
            
        # Calculate nutrition needs
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
    """Save user profile data to MongoDB."""
    try:
        data = request.json
        
        # Extract user data
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
        
        # Basic validation
        if not user_data["email"] or not user_data["full_name"]:
            return jsonify({'error': 'Email and full name are required'}), 400
            
        # Save user data to MongoDB
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
    """Process chat messages and return AI responses using Google's Gemini API."""
    try:
        data = request.json
        message = data.get('message', '')
        nutrition_data = data.get('nutritionData', {})
        chat_history = data.get('chatHistory', [])
        
        # Get AI response from Gemini
        response = get_gemini_response(message, nutrition_data, chat_history)
        
        return jsonify({'response': response})
    
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'response': 'Sorry, I encountered an error processing your request. Please try again.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from utils import calculate_nutrition, get_openai_response
from database import init_db
from mongo_db import init_mongodb, save_user, get_user_by_email

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize databases
init_db(app)
init_mongodb()

@app.route('/')
def index():
    """Render the main page with the chat interface."""
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
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
def chat():
    """Process chat messages and return AI responses."""
    try:
        data = request.json
        message = data.get('message', '')
        nutrition_data = data.get('nutritionData', {})
        chat_history = data.get('chatHistory', [])
        
        # Get AI response
        response = get_openai_response(message, nutrition_data, chat_history)
        
        return jsonify({'response': response})
    
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'response': 'Sorry, I encountered an error processing your request. Please try again.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

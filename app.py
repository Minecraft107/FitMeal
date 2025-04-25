import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from utils import calculate_nutrition, get_openai_response

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

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

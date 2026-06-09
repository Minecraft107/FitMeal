import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from .models import save_profile
from .services.nutrition import calculate_nutrition
from .services.gemini import get_chat_response

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    return render_template('index_extended.html')


@main_bp.route('/calculate', methods=['POST'])
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

        result = calculate_nutrition(
            height, weight, age, gender,
            activity_level, goal, diet_type, metabolic_type
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"calculate error: {e}")
        return jsonify({'error': 'Calculation failed'}), 500


@main_bp.route('/save-user', methods=['POST'])
@login_required
def save_user_profile():
    try:
        data = request.json
        profile = {
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
            "updated_at": datetime.utcnow().isoformat(),
        }

        if not profile["email"] or not profile["full_name"]:
            return jsonify({'error': 'Email and full name required'}), 400

        if save_profile(profile):
            return jsonify({'success': True, 'message': 'Profile saved'})
        return jsonify({'success': False, 'message': 'Failed to save profile'}), 500

    except Exception as e:
        logger.error(f"save_user_profile error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@main_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.json
        response = get_chat_response(
            data.get('message', ''),
            data.get('nutritionData', {}),
            data.get('chatHistory', []),
        )
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"chat error: {e}")
        return jsonify({'response': 'An error occurred.'}), 500

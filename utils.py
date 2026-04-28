import os
import json
import logging
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def calculate_bmr(weight, height, age, gender):
    """
    Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation.
    
    Args:
        weight (float): Weight in kg
        height (float): Height in cm
        age (int): Age in years
        gender (str): 'male' or 'female'
        
    Returns:
        float: Basal Metabolic Rate in calories
    """
    if gender.lower() == 'male':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    return bmr

def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure based on activity level.
    
    Args:
        bmr (float): Basal Metabolic Rate
        activity_level (str): Activity level category
        
    Returns:
        float: Total Daily Energy Expenditure in calories
    """
    activity_multipliers = {
        'sedentary': 1.2,  # Little or no exercise
        'lightly_active': 1.375,  # Light exercise/sports 1-3 days/week
        'moderately_active': 1.55,  # Moderate exercise/sports 3-5 days/week
        'very_active': 1.725,  # Hard exercise/sports 6-7 days/week
        'extra_active': 1.9  # Very hard exercise, physical job or training twice a day
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.2)
    return bmr * multiplier

def adjust_for_goal(tdee, goal):
    """
    Adjust calorie intake based on fitness goal.
    
    Args:
        tdee (float): Total Daily Energy Expenditure
        goal (str): 'lose', 'maintain', or 'gain'
        
    Returns:
        float: Adjusted calorie intake
    """
    goal_adjustments = {
        'lose': 0.8,  # 20% deficit for weight loss
        'maintain': 1.0,  # Maintain current weight
        'gain': 1.15  # 15% surplus for muscle gain
    }
    
    adjustment = goal_adjustments.get(goal, 1.0)
    return tdee * adjustment

def adjust_for_metabolic_type(calories, macros, metabolic_type):
    """
    Adjust macronutrient distribution based on metabolic type.
    
    Args:
        calories (float): Total daily calories
        macros (dict): Original macronutrient distribution
        metabolic_type (str): 'fast', 'slow', or 'mixed'
        
    Returns:
        dict: Adjusted macronutrient distribution
    """
    # Default macros stays the same if metabolic_type is 'mixed'
    if metabolic_type == 'fast':
        # For fast metabolism, increase carbs, moderate protein
        return {
            'protein': round(calories * 0.25 / 4),  # 25% protein
            'carbs': round(calories * 0.55 / 4),    # 55% carbs
            'fat': round(calories * 0.20 / 9)       # 20% fat
        }
    elif metabolic_type == 'slow':
        # For slow metabolism, increase protein, lower carbs
        return {
            'protein': round(calories * 0.35 / 4),  # 35% protein
            'carbs': round(calories * 0.35 / 4),    # 35% carbs
            'fat': round(calories * 0.30 / 9)       # 30% fat
        }
    
    # For mixed, return original macros
    return macros

def adjust_for_diet_type(macros, diet_type):
    """
    Adjust macronutrient distribution based on diet type.
    
    Args:
        macros (dict): Original macronutrient distribution
        diet_type (str): Diet type (balanced, keto, etc.)
        
    Returns:
        dict: Adjusted macronutrient distribution
    """
    total_calories = (macros['protein'] * 4) + (macros['carbs'] * 4) + (macros['fat'] * 9)
    
    if diet_type == 'keto':
        return {
            'protein': round(total_calories * 0.25 / 4),  # 25% protein
            'carbs': round(total_calories * 0.05 / 4),    # 5% carbs
            'fat': round(total_calories * 0.70 / 9)       # 70% fat
        }
    elif diet_type == 'high_protein':
        return {
            'protein': round(total_calories * 0.40 / 4),  # 40% protein
            'carbs': round(total_calories * 0.30 / 4),    # 30% carbs
            'fat': round(total_calories * 0.30 / 9)       # 30% fat
        }
    elif diet_type == 'low_fat':
        return {
            'protein': round(total_calories * 0.30 / 4),  # 30% protein
            'carbs': round(total_calories * 0.55 / 4),    # 55% carbs
            'fat': round(total_calories * 0.15 / 9)       # 15% fat
        }
    elif diet_type == 'vegan':
        return {
            'protein': round(total_calories * 0.20 / 4),  # 20% protein
            'carbs': round(total_calories * 0.60 / 4),    # 60% carbs
            'fat': round(total_calories * 0.20 / 9)       # 20% fat
        }
    
    # Default balanced diet
    return {
        'protein': round(total_calories * 0.30 / 4),  # 30% protein
        'carbs': round(total_calories * 0.45 / 4),    # 45% carbs
        'fat': round(total_calories * 0.25 / 9)       # 25% fat
    }

def calculate_nutrition(height, weight, age, gender, activity_level, goal, diet_type, metabolic_type):
    """
    Calculate daily calorie and macronutrient needs.
    
    Args:
        height (float): Height in cm
        weight (float): Weight in kg
        age (int): Age in years
        gender (str): 'male' or 'female'
        activity_level (str): Activity level category
        goal (str): 'lose', 'maintain', or 'gain'
        diet_type (str): Diet type (balanced, keto, etc.)
        metabolic_type (str): 'fast', 'slow', or 'mixed'
        
    Returns:
        dict: Nutrition data including calories and macronutrients
    """
    # Calculate BMR
    bmr = calculate_bmr(weight, height, age, gender)
    
    # Calculate TDEE
    tdee = calculate_tdee(bmr, activity_level)
    
    # Adjust for goal
    adjusted_calories = adjust_for_goal(tdee, goal)
    
    # Calculate baseline macros (balanced)
    baseline_macros = {
        'protein': round(adjusted_calories * 0.30 / 4),  # 30% protein
        'carbs': round(adjusted_calories * 0.45 / 4),    # 45% carbs
        'fat': round(adjusted_calories * 0.25 / 9)       # 25% fat
    }
    
    # Adjust for diet type
    diet_adjusted_macros = adjust_for_diet_type(baseline_macros, diet_type)
    
    # Adjust for metabolic type
    final_macros = adjust_for_metabolic_type(adjusted_calories, diet_adjusted_macros, metabolic_type)
    
    # Package results
    nutrition_data = {
        'bmr': round(bmr),
        'tdee': round(tdee),
        'daily_calories': round(adjusted_calories),
        'macros': final_macros,
        'user_info': {
            'height': height,
            'weight': weight,
            'age': age,
            'gender': gender,
            'activity_level': activity_level,
            'goal': goal,
            'diet_type': diet_type,
            'metabolic_type': metabolic_type
        }
    }
    
    return nutrition_data

def get_openai_response(message, nutrition_data, chat_history):
    """
    Get AI response from OpenAI API.
    
    Args:
        message (str): User message
        nutrition_data (dict): User's nutrition data
        chat_history (list): Previous chat messages
        
    Returns:
        str: AI response
    """
    try:
        # Prepare system message with nutrition data context
        system_message = f"""
        You are an AI nutrition assistant. Your goal is to provide helpful, personalized nutrition advice.
        
        USER'S NUTRITION DATA:
        - Daily Calories: {nutrition_data.get('daily_calories', 'Not provided')} calories
        - Protein: {nutrition_data.get('macros', {}).get('protein', 'Not provided')}g
        - Carbohydrates: {nutrition_data.get('macros', {}).get('carbs', 'Not provided')}g
        - Fat: {nutrition_data.get('macros', {}).get('fat', 'Not provided')}g
        
        USER INFO:
        - Height: {nutrition_data.get('user_info', {}).get('height', 'Not provided')} cm
        - Weight: {nutrition_data.get('user_info', {}).get('weight', 'Not provided')} kg
        - Age: {nutrition_data.get('user_info', {}).get('age', 'Not provided')} years
        - Gender: {nutrition_data.get('user_info', {}).get('gender', 'Not provided')}
        - Activity Level: {nutrition_data.get('user_info', {}).get('activity_level', 'Not provided')}
        - Goal: {nutrition_data.get('user_info', {}).get('goal', 'Not provided')}
        - Diet Type: {nutrition_data.get('user_info', {}).get('diet_type', 'Not provided')}
        - Metabolic Type: {nutrition_data.get('user_info', {}).get('metabolic_type', 'Not provided')}
        
        Provide concise, helpful advice based on this information. Focus on practical tips, meal ideas, 
        and strategies that align with their goals and preferences. Avoid giving medical advice.
        """
        
        # Prepare messages for the API call
        messages = [{"role": "system", "content": system_message}]
        
        # Add chat history (limited to last 10 messages to stay within token limits)
        for item in chat_history[-10:]:
            role = "assistant" if item.get("isBot") else "user"
            messages.append({"role": role, "content": item.get("message", "")})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Make OpenAI API call
        response = openai.chat.completions.create(
            model="gpt-4o",  # Using the latest model
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract and return response
        return response.choices[0].message.content
    
    except Exception as e:
        logging.error(f"Error getting OpenAI response: {str(e)}")
        return "I'm sorry, I'm having trouble processing your request at the moment. Please try again later."

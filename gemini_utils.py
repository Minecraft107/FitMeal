"""
Utility functions for working with Google's Gemini API.
"""
import os
import logging
import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Configure the Gemini API with the API key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logging.warning("GEMINI_API_KEY not found in environment variables")

def get_gemini_response(message, nutrition_data, chat_history):
    """
    Get AI response from Google Gemini API.
    
    Args:
        message (str): User message
        nutrition_data (dict): User's nutrition data
        chat_history (list): Previous chat messages
        
    Returns:
        str: AI response
    """
    try:
        if not GEMINI_API_KEY:
            return "To use the chatbot functionality, please provide a valid Google Gemini API key as environment variable GEMINI_API_KEY."
        
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
        
        # Initialize Gemini model
        # Using the Gemini Pro model which is suitable for text-only interactions
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare chat history in Gemini format
        chat = model.start_chat(history=[])
        
        # Add the system prompt to set context
        chat.send_message(system_message)
        
        # Add chat history
        for item in chat_history[-5:]:  # Limit to last 5 messages to avoid token issues
            role = "model" if item.get("isBot") else "user"
            if role == "model":
                chat.history.append({"role": role, "parts": [item.get("message", "")]})
            else:
                chat.send_message(item.get("message", ""))
        
        # Get response for current message
        response = chat.send_message(message)
        
        return response.text
    
    except Exception as e:
        logging.error(f"Error getting Gemini response: {str(e)}")
        return "I'm sorry, I'm having trouble processing your request at the moment. Please try again later."
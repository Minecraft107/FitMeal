import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found")


def get_chat_response(message, nutrition_data, chat_history):
    if not API_KEY:
        return "Chatbot requires a GEMINI_API_KEY environment variable."

    try:
        system = f"""
You are an AI nutrition assistant.

USER'S NUTRITION DATA:
- Daily Calories: {nutrition_data.get('daily_calories', 'N/A')}
- Protein: {nutrition_data.get('macros', {}).get('protein', 'N/A')}g
- Carbs: {nutrition_data.get('macros', {}).get('carbs', 'N/A')}g
- Fat: {nutrition_data.get('macros', {}).get('fat', 'N/A')}g

USER INFO:
- Height: {nutrition_data.get('user_info', {}).get('height', 'N/A')} cm
- Weight: {nutrition_data.get('user_info', {}).get('weight', 'N/A')} kg
- Age: {nutrition_data.get('user_info', {}).get('age', 'N/A')}
- Gender: {nutrition_data.get('user_info', {}).get('gender', 'N/A')}
- Activity: {nutrition_data.get('user_info', {}).get('activity_level', 'N/A')}
- Goal: {nutrition_data.get('user_info', {}).get('goal', 'N/A')}
- Diet: {nutrition_data.get('user_info', {}).get('diet_type', 'N/A')}
- Metabolic Type: {nutrition_data.get('user_info', {}).get('metabolic_type', 'N/A')}

Give concise, practical nutrition advice. No medical advice.
"""

        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=[])
        chat.send_message(system)

        for item in chat_history[-5:]:
            if item.get("isBot"):
                chat.history.append({"role": "model", "parts": [item["message"]]})
            else:
                chat.send_message(item["message"])

        return chat.send_message(message).text

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return "Sorry, I'm having trouble processing your request."

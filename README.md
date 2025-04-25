# AI Nutrition Assistant

An AI-powered nutrition assistant chatbot with personalized calorie and macronutrient calculations.

## Features

- User authentication system (login/registration)
- Personalized nutrition calculations based on:
  - Personal details (height, weight, age, gender)
  - Activity level
  - Fitness goals
  - Diet preferences
  - Metabolic type
- Interactive chat interface with AI-powered responses
- MongoDB storage for user profiles
- PostgreSQL database for user accounts and chat history

## Setup Instructions for VS Code

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- MongoDB (optional, falls back to in-memory storage if not available)
- OpenAI API key for chat functionality

### Installation

1. **Clone the repository or create a new folder** and copy all the files

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install email-validator flask flask-login flask-sqlalchemy flask-wtf gunicorn openai psycopg2-binary pymongo
   ```

5. **Set up environment variables**
   - Create a `.env` file based on the provided `.env.example`
   - Add your database connection strings and API keys

6. **Set up PostgreSQL database**
   - Create a new database for the application
   - Update the `DATABASE_URL` in your `.env` file

7. **Run the application**
   ```bash
   python main.py
   ```

8. **Access the application**
   - Open a web browser and go to `http://localhost:5000`

## File Structure

```
nutrition-assistant/
├── static/
│   ├── css/
│   │   └── custom.css
│   └── js/
│       └── script.js
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── index_extended.html
│   ├── login.html
│   └── register.html
├── .env
├── .env.example
├── app.py
├── database.py
├── main.py
├── models.py
├── mongo_db.py
├── README.md
└── utils.py
```

## Environment Variables

- `SESSION_SECRET`: Secret key for Flask sessions
- `DATABASE_URL`: PostgreSQL connection string
- `MONGODB_URI`: MongoDB connection string (optional)
- `OPENAI_API_KEY`: OpenAI API key for chat responses

## Features in Detail

### User Authentication

- Secure user registration and login
- Password hashing for security
- Session management with Flask-Login

### Nutrition Calculation

- BMR (Basal Metabolic Rate) calculation using the Mifflin-St Jeor Equation
- TDEE (Total Daily Energy Expenditure) based on activity level
- Macronutrient distribution based on:
  - Diet type (balanced, high protein, keto, low fat, vegan)
  - Metabolic type (fast, slow, mixed)
  - Fitness goals (lose, maintain, gain)

### Chat Interface

- Interactive chat with AI-powered responses
- Context-aware responses based on user's nutrition profile
- Personalized nutrition advice
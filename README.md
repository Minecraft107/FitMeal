# AI Nutrition Assistant (FitMeal)

An AI-powered nutrition assistant chatbot with user authentication and personalized calorie/macronutrient calculations.

## Features

- **User authentication** — register, login, session management (Flask-Login)
- **Personalized nutrition calculations** based on:
  - Personal details (height, weight, age, gender)
  - Activity level, fitness goals, diet preferences, metabolic type
- **Interactive AI chat** powered by Google Gemini API
- **MongoDB storage** for user profiles (local MongoDB or Atlas)
- **In-memory fallback** — works without MongoDB

## Local Development

### Prerequisites

- Python 3.11+
- MongoDB Compass or MongoDB Atlas (optional — falls back to in-memory)

### Setup

```bash
# 1. Clone and enter the project
cd FitMeal

# 2. Create & activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate         # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your settings (or run: python local_setup.py)

# 5. Run the app
python main.py
```

Open **http://localhost:5000** — you'll be redirected to the login page.

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SESSION_SECRET` | **Yes** | Flask session signing key |
| `MONGODB_URI` | No | MongoDB connection string (omit for in-memory) |
| `GEMINI_API_KEY` | No | Google Gemini API key for chat |

## Deploy to Render (GitHub Auto-Deploy)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/FitMeal.git
git branch -M main
git push -u origin main
```

### 2. Set up on Render

1. Go to **https://dashboard.render.com** → **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `fitmeal`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:5000 main:app`
   - **Python Version**: 3.11

### 3. Add Environment Variables in Render Dashboard

| Key | Value |
|---|---|
| `SESSION_SECRET` | (generate a random hex string) |
| `MONGODB_URI` | Your MongoDB Atlas connection string |
| `GEMINI_API_KEY` | (optional) Your Gemini API key |

### 4. Deploy

Click **Create Web Service** — Render will build and deploy automatically.

## MongoDB Setup

### Local (MongoDB Compass)

1. Install MongoDB Compass and run a local server
2. Set `MONGODB_URI=mongodb://localhost:27017/fitmeal` in `.env`

### Production (MongoDB Atlas — free tier)

1. Create a free cluster at **https://cloud.mongodb.com**
2. Create a database user, allow network access from everywhere (`0.0.0.0/0`)
3. Get your connection string and set as `MONGODB_URI` on Render

## Project Structure

```
FitMeal/
├── static/
│   ├── css/custom.css
│   └── js/script.js
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── index_extended.html
│   ├── login.html
│   └── register.html
├── .env.example
├── .gitignore
├── app.py
├── database.py
├── gemini_utils.py
├── local_setup.py
├── main.py
├── models.py
├── mongo_db.py
├── requirements.txt
├── utils.py
└── pyproject.toml
```

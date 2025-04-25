from datetime import datetime
from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for storing user information"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(120))
    location = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    nutrition_profiles = db.relationship('NutritionProfile', backref='user', lazy=True, cascade="all, delete-orphan")
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check password against stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class NutritionProfile(db.Model):
    """Model for storing user nutrition profiles"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False, default="Default Profile")
    height = db.Column(db.Float, nullable=False)  # in cm
    weight = db.Column(db.Float, nullable=False)  # in kg
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    activity_level = db.Column(db.String(30), nullable=False)
    goal = db.Column(db.String(20), nullable=False)
    diet_type = db.Column(db.String(30), nullable=False)
    metabolic_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Calculated fields
    bmr = db.Column(db.Integer)
    tdee = db.Column(db.Integer)
    daily_calories = db.Column(db.Integer)
    protein_grams = db.Column(db.Integer)
    carbs_grams = db.Column(db.Integer)
    fat_grams = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<NutritionProfile {self.name} - User {self.user_id}>'
    
    def to_dict(self):
        """Convert profile to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'height': self.height,
            'weight': self.weight,
            'age': self.age,
            'gender': self.gender,
            'activity_level': self.activity_level,
            'goal': self.goal,
            'diet_type': self.diet_type,
            'metabolic_type': self.metabolic_type,
            'bmr': self.bmr,
            'tdee': self.tdee,
            'daily_calories': self.daily_calories,
            'macros': {
                'protein': self.protein_grams,
                'carbs': self.carbs_grams,
                'fat': self.fat_grams
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ChatSession(db.Model):
    """Model for storing chat sessions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nutrition_profile_id = db.Column(db.Integer, db.ForeignKey('nutrition_profile.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade="all, delete-orphan", order_by="ChatMessage.timestamp")
    
    def __repr__(self):
        return f'<ChatSession {self.id} - User {self.user_id}>'

class ChatMessage(db.Model):
    """Model for storing chat messages"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_bot = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.id} - {"Bot" if self.is_bot else "User"}>'
    
    def to_dict(self):
        """Convert message to dictionary for API responses"""
        return {
            'id': self.id,
            'content': self.content,
            'is_bot': self.is_bot,
            'timestamp': self.timestamp.isoformat()
        }
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import json
import os
from fpdf import FPDF
from docx import Document
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizgenix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    questions = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            name=data.get('name'),
            email=data.get('email'),
            password_hash=generate_password_hash(data.get('password')),
            role=data.get('role', 'student')
        )
        
        db.session.add(user)
        db.session.commit()
        
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user and check_password_hash(user.password_hash, data.get('password')):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
            }, app.config['SECRET_KEY'])
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role
                }
            })
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz', methods=['POST'])
def create_quiz():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        quiz_data = request.get_json()
        
        # Generate sample questions (replace with actual AI generation)
        questions = generate_sample_questions(quiz_data)
        
        quiz = Quiz(
            user_id=user_id,
            title=quiz_data.get('title'),
            subject=quiz_data.get('subject'),
            topic=quiz_data.get('topic'),
            difficulty=quiz_data.get('difficulty'),
            questions=json.dumps(questions)
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({
            'id': quiz.id,
            'title': quiz.title,
            'subject': quiz.subject,
            'topic': quiz.topic,
            'difficulty': quiz.difficulty,
            'questions': questions,
            'created_at': quiz.created_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_sample_questions(quiz_data):
    """Generate sample questions based on quiz parameters"""
    questions = []
    count = int(quiz_data.get('questionCount', 5))
    
    for i in range(count):
        question = {
            'question': f"Sample question {i+1} about {quiz_data.get('topic')}?",
            'options': [
                f"Option A for question {i+1}",
                f"Option B for question {i+1}",
                f"Option C for question {i+1}",
                f"Option D for question {i+1}"
            ],
            'correct_answer': f"Option A for question {i+1}"
        }
        questions.append(question)
    
    return questions

@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        quizzes = Quiz.query.filter_by(user_id=user_id).all()
        
        quiz_list = []
        for quiz in quizzes:
            quiz_list.append({
                'id': quiz.id,
                'title': quiz.title,
                'subject': quiz.subject,
                'topic': quiz.topic,
                'difficulty': quiz.difficulty,
                'questions': json.loads(quiz.questions),
                'created_at': quiz.created_at.isoformat()
            })
        
        return jsonify({'quizzes': quiz_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def init_db():
    """Initialize database with sample data"""
    db.create_all()
    
    # Create test users if they don't exist
    if not User.query.filter_by(email='lecturer@test.com').first():
        lecturer = User(
            name='Test Lecturer',
            email='lecturer@test.com',
            password_hash=generate_password_hash('password123'),
            role='lecturer'
        )
        db.session.add(lecturer)
    
    if not User.query.filter_by(email='student@test.com').first():
        student = User(
            name='Test Student',
            email='student@test.com',
            password_hash=generate_password_hash('password123'),
            role='student'
        )
        db.session.add(student)
    
    db.session.commit()
    print("✅ Database initialized with test users")

if __name__ == '__main__':
    print("🚀 Starting Quizgenix Backend...")
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
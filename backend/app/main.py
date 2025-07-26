import os
import json
import requests
import random
import jwt
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Secret key for JWT tokens
JWT_SECRET = os.getenv('JWT_SECRET', 'quizgenix-super-secret-key-2024')

# Simple in-memory storage (in production, use a proper database)
users = {}
quizzes = {}
grades = {}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = users.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            print(f"Token error: {e}")
            return jsonify({'error': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return "Quizgenix backend running successfully! 🚀"

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        role = data.get('role', 'student')
        
        print(f"Registration attempt: {email}, {name}, {role}")
        
        if not email or not password or not name:
            return jsonify({"error": "Missing required fields"}), 400
        
        if email in users:
            return jsonify({"error": "User already exists"}), 400
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user_id = str(len(users) + 1)
        user = {
            'id': user_id,
            'email': email,
            'name': name,
            'role': role,
            'password_hash': password_hash,
            'created_at': datetime.now().isoformat()
        }
        
        users[email] = user
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256')
        
        # Return user data without password
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        print(f"User registered successfully: {email}")
        
        return jsonify({
            "message": "User registered successfully",
            "user": user_data,
            "token": token
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        print(f"Login attempt: {email}")
        
        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400
        
        user = users.get(email)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user['password_hash'] != password_hash:
            return jsonify({"error": "Invalid password"}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256')
        
        # Return user data without password
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        print(f"Login successful: {email}")
        
        return jsonify({
            "message": "Login successful",
            "user": user_data,
            "token": token
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/quiz', methods=['POST'])
@token_required
def generate_quiz(current_user):
    try:
        data = request.get_json()
        topic = data.get('topic', 'General Knowledge')
        num_questions = data.get('num_questions', 5)
        difficulty = data.get('difficulty', 'medium')
        
        print(f"Generating quiz: {topic}, {num_questions} questions, {difficulty}")
        
        # Generate questions using the existing logic
        questions = []
        for i in range(num_questions):
            question = generate_smart_template_question(topic, i)
            question['questionId'] = i + 1
            questions.append(question)
        
        # Store quiz
        quiz_id = str(len(quizzes) + 1)
        quiz_data = {
            'id': quiz_id,
            'topic': topic,
            'num_questions': num_questions,
            'difficulty': difficulty,
            'questions': questions,
            'created_by': current_user['id'],
            'created_by_name': current_user['name'],
            'created_at': datetime.now().isoformat()
        }
        quizzes[quiz_id] = quiz_data
        
        print(f"Quiz created successfully: ID {quiz_id}")
        
        return jsonify({
            "questions": questions,
            "total_questions": len(questions),
            "topic": topic,
            "quiz_id": quiz_id,
            "message": f"Generated {len(questions)} questions for {topic}"
        }), 200
        
    except Exception as e:
        print(f"Quiz generation error: {e}")
        return jsonify({"error": "Failed to generate quiz"}), 500

@app.route('/api/score', methods=['POST'])
@token_required
def calculate_score(current_user):
    try:
        data = request.get_json()
        questions = data.get('questions', [])
        user_answers = data.get('user_answers', [])
        topic = data.get('topic', 'Unknown')
        
        if not questions or not user_answers:
            return jsonify({"error": "Missing questions or answers"}), 400
            
        total_questions = len(questions)
        correct_answers = 0
        detailed_results = []
        
        for i, question in enumerate(questions):
            user_answer = user_answers[i] if i < len(user_answers) else -1
            correct_option = question.get('correctOption', 0)
            is_correct = user_answer == correct_option
            
            if is_correct:
                correct_answers += 1
                
            result = {
                "questionId": question.get('questionId', i + 1),
                "question": question.get('question', ''),
                "user_answer": user_answer,
                "correct_answer": correct_option,
                "is_correct": is_correct,
                "options": question.get('options', []),
                "source": question.get('source', ''),
                "explanation": generate_explanation(question, is_correct)
            }
            detailed_results.append(result)
        
        score_percentage = (correct_answers / total_questions) * 100
        
        # Determine performance level
        if score_percentage >= 90:
            performance = "Excellent! 🏆"
        elif score_percentage >= 70:
            performance = "Good Job! 👍"
        elif score_percentage >= 50:
            performance = "Not Bad! 📚"
        else:
            performance = "Keep Learning! 💪"
        
        # Store grade for lecturer access
        grade_id = str(len(grades) + 1)
        grade_record = {
            'id': grade_id,
            'user_id': current_user['id'],
            'user_name': current_user['name'],
            'user_email': current_user['email'],
            'topic': topic,
            'score': correct_answers,
            'total': total_questions,
            'percentage': round(score_percentage, 1),
            'completed_at': datetime.now().isoformat(),
            'results': detailed_results
        }
        grades[grade_id] = grade_record
            
        return jsonify({
            "score": {
                "correct": correct_answers,
                "total": total_questions,
                "percentage": round(score_percentage, 1),
                "performance": performance
            },
            "results": detailed_results,
            "study_resources": generate_study_resources(topic)
        })
        
    except Exception as e:
        print(f"Error calculating score: {e}")
        return jsonify({"error": "Failed to calculate score"}), 500

# Lecturer-specific endpoints
@app.route('/api/lecturer/quizzes', methods=['GET'])
@token_required
def get_lecturer_quizzes(current_user):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    lecturer_quizzes = [q for q in quizzes.values() if q.get('created_by') == current_user['id']]
    return jsonify({'quizzes': lecturer_quizzes})

@app.route('/api/lecturer/students', methods=['GET'])
@token_required
def get_students(current_user):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    students = [u for u in users.values() if u['role'] == 'student']
    safe_students = [{k: v for k, v in student.items() if k != 'password_hash'} for student in students]
    return jsonify({'students': safe_students})

@app.route('/api/lecturer/grades', methods=['GET'])
@token_required
def get_grades(current_user):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    all_grades = list(grades.values())
    return jsonify({'grades': all_grades})

@app.route('/api/lecturer/grades/download', methods=['GET'])
@token_required
def download_grades(current_user):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    format_type = request.args.get('format', 'csv')
    
    import io
    from flask import make_response
    
    output = io.StringIO()
    output.write('Student Name,Email,Topic,Score,Total,Percentage,Date\n')
    
    for grade in grades.values():
        output.write(f"{grade['user_name']},{grade['user_email']},{grade['topic']},{grade['score']},{grade['total']},{grade['percentage']}%,{grade['completed_at']}\n")
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=grades.csv'
    
    return response

@app.route('/api/quiz/<quiz_id>/download', methods=['GET'])
@token_required
def download_quiz(current_user, quiz_id):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    format_type = request.args.get('format', 'pdf')
    quiz = quizzes.get(quiz_id)
    
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    from flask import make_response
    
    # Generate quiz content
    quiz_content = f"Quiz: {quiz['topic']}\n"
    quiz_content += f"Questions: {quiz['num_questions']}\n"
    quiz_content += f"Created by: {quiz['created_by_name']}\n\n"
    
    for i, q in enumerate(quiz['questions'], 1):
        quiz_content += f"Question {i}: {q['question']}\n"
        for j, option in enumerate(q['options']):
            quiz_content += f"  {chr(65+j)}) {option}\n"
        quiz_content += f"Correct Answer: {chr(65+q['correctOption'])}\n\n"
    
    response = make_response(quiz_content)
    if format_type == 'pdf':
        response.headers['Content-Type'] = 'application/pdf'
    elif format_type == 'docx':
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    else:
        response.headers['Content-Type'] = 'text/plain'
    
    response.headers['Content-Disposition'] = f'attachment; filename=quiz_{quiz_id}.{format_type}'
    return response

@app.route('/api/student/quizzes', methods=['GET'])
@token_required
def get_student_quizzes(current_user):
    if current_user['role'] != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    available_quizzes = list(quizzes.values())
    return jsonify({'quizzes': available_quizzes})

# Helper functions
def generate_smart_template_question(topic, question_index=0):
    templates = [
        f"What is the most important aspect of {topic}?",
        f"Which field is {topic} primarily associated with?",
        f"What is the main benefit of studying {topic}?",
        f"Which concept is fundamental to {topic}?",
        f"What skill is essential for {topic}?"
    ]
    
    options_sets = [
        ["Core concept", "Secondary idea", "Related topic", "Advanced application"],
        ["Primary field", "Supporting area", "Adjacent domain", "Unrelated field"],
        ["Main benefit", "Minor advantage", "Side effect", "Potential drawback"],
        ["Key principle", "Basic rule", "Complex theory", "Simple fact"],
        ["Essential skill", "Helpful ability", "Optional knowledge", "Advanced technique"]
    ]
    
    template_index = question_index % len(templates)
    
    return {
        "question": templates[template_index],
        "options": options_sets[template_index],
        "correctOption": 0,
        "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
        "difficulty": ["easy", "medium", "hard"][question_index % 3]
    }

def generate_explanation(question, is_correct):
    if is_correct:
        return "Excellent! You got this right."
    else:
        return "Not quite right. Check the source link to learn more."

def generate_study_resources(topic):
    return [
        {
            "title": f"Wikipedia: {topic}",
            "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "type": "encyclopedia"
        },
        {
            "title": f"Khan Academy: {topic}",
            "url": f"https://www.khanacademy.org/search?query={topic.replace(' ', '+')}",
            "type": "educational"
        }
    ]

if __name__ == '__main__':
    # Initialize test users
    test_users = {
        'lecturer@test.com': {
            'id': '1',
            'email': 'lecturer@test.com',
            'password_hash': hashlib.sha256('password123'.encode()).hexdigest(),
            'name': 'Test Lecturer',
            'role': 'lecturer',
            'created_at': datetime.now().isoformat()
        },
        'student@test.com': {
            'id': '2',
            'email': 'student@test.com',
            'password_hash': hashlib.sha256('password123'.encode()).hexdigest(),
            'name': 'Test Student',
            'role': 'student',
            'created_at': datetime.now().isoformat()
        }
    }
    
    users.update(test_users)
    
    print("🚀 Starting Quizgenix Backend Server...")
    print("📧 Test Accounts:")
    print("   Lecturer: lecturer@test.com / password123")
    print("   Student: student@test.com / password123")
    print("🌐 Backend running on: http://127.0.0.1:5000")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
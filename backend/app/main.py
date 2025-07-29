import os
import json
import requests
import random
import jwt
import hashlib
import io
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

# Try to import optional libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("OpenAI not available - using template questions")

try:
    import wikipedia
    HAS_WIKIPEDIA = True
except ImportError:
    HAS_WIKIPEDIA = False
    print("Wikipedia not available - using basic templates")

load_dotenv()

app = Flask(__name__)
CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Secret key for JWT tokens
JWT_SECRET = os.getenv('JWT_SECRET', 'quizgenix-super-secret-key-2024')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id')

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

# Helper functions - Add these before the routes
def generate_smart_template_question(topic, question_index):
    """Generate template questions when advanced generation fails"""
    templates = [
        {
            "question": f"What is the primary characteristic of {topic}?",
            "options": [
                f"It is fundamental to understanding {topic}",
                f"It is rarely used in {topic}",
                f"It contradicts {topic} principles",
                f"It is unrelated to {topic}"
            ],
            "correctOption": 0,
            "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "difficulty": "medium"
        },
        {
            "question": f"Which statement best describes {topic}?",
            "options": [
                f"{topic} is an important concept in its field",
                f"{topic} is completely outdated",
                f"{topic} has no practical applications",
                f"{topic} is purely theoretical"
            ],
            "correctOption": 0,
            "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "difficulty": "medium"
        },
        {
            "question": f"What is a key application of {topic}?",
            "options": [
                f"Practical implementation in real-world scenarios",
                f"Only used in theoretical discussions",
                f"Has no real applications",
                f"Used only in historical contexts"
            ],
            "correctOption": 0,
            "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "difficulty": "medium"
        }
    ]
    
    return templates[question_index % len(templates)]

def generate_detailed_explanation(question, is_correct, user_answer):
    """Generate detailed explanations for answers"""
    if is_correct:
        return f"Correct! {question['options'][question['correctOption']]} is indeed the right answer."
    else:
        correct_text = question['options'][question['correctOption']]
        if user_answer >= 0 and user_answer < len(question['options']):
            user_text = question['options'][user_answer]
            return f"Not quite right. You selected '{user_text}', but the correct answer is '{correct_text}'. {question.get('context', 'Check the source link to learn more.')}"
        else:
            return f"No answer selected. The correct answer is '{correct_text}'. {question.get('context', 'Check the source link to learn more.')}"

def calculate_performance_metrics(score_percentage, time_taken, time_limit):
    """Calculate detailed performance metrics"""
    # Time efficiency (how much time was used)
    time_efficiency = (time_taken / time_limit) * 100 if time_limit > 0 else 100
    
    # Performance level based on score and time
    if score_percentage >= 90:
        if time_efficiency <= 75:
            level = "Excellent & Efficient! 🏆⚡"
        else:
            level = "Excellent! 🏆"
    elif score_percentage >= 80:
        if time_efficiency <= 75:
            level = "Very Good & Fast! 🎯⚡"
        else:
            level = "Very Good! 🎯"
    elif score_percentage >= 70:
        level = "Good Job! 👍"
    elif score_percentage >= 60:
        level = "Not Bad! 📚"
    elif score_percentage >= 50:
        level = "Keep Learning! 💪"
    else:
        level = "More Practice Needed! 📖"
    
    return {
        'level': level,
        'time_efficiency': round(time_efficiency, 1),
        'score_grade': get_letter_grade(score_percentage)
    }

def get_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'

def generate_advanced_quiz_questions(topic, num_questions, difficulty):
    """Generate questions using multiple sources"""
    questions = []
    
    try:
        # Try to get Wikipedia content for context if available
        if HAS_WIKIPEDIA:
            wiki_summary = wikipedia.summary(topic, sentences=3)
        else:
            wiki_summary = f"Learn more about {topic}"
        
        # Generate questions based on topic and difficulty
        for i in range(num_questions):
            if HAS_WIKIPEDIA and i % 2 == 0:
                # Factual questions
                question = generate_factual_question(topic, wiki_summary, difficulty)
            else:
                # Conceptual questions or template questions
                if HAS_WIKIPEDIA:
                    question = generate_conceptual_question(topic, difficulty)
                else:
                    question = generate_smart_template_question(topic, i)
            
            question['questionId'] = i + 1
            questions.append(question)
            
    except Exception as e:
        print(f"Advanced generation failed, using templates: {e}")
        # Fallback to template questions
        for i in range(num_questions):
            question = generate_smart_template_question(topic, i)
            question['questionId'] = i + 1
            questions.append(question)
    
    return questions

def generate_factual_question(topic, context, difficulty):
    """Generate factual questions based on topic and context"""
    question_templates = {
        'easy': [
            f"What is {topic}?",
            f"Where is {topic} commonly found?",
            f"When was {topic} first discovered/invented?"
        ],
        'medium': [
            f"What are the main characteristics of {topic}?",
            f"How does {topic} relate to its field of study?",
            f"What are the primary applications of {topic}?"
        ],
        'hard': [
            f"What are the theoretical implications of {topic}?",
            f"How does {topic} compare to similar concepts?",
            f"What are the advanced principles behind {topic}?"
        ]
    }
    
    questions = question_templates.get(difficulty, question_templates['medium'])
    selected_question = random.choice(questions)
    
    # Generate contextual options
    options = generate_contextual_options(topic, difficulty)
    
    return {
        "question": selected_question,
        "options": options,
        "correctOption": 0,
        "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
        "difficulty": difficulty,
        "context": context[:200] + "..." if len(context) > 200 else context
    }

def generate_conceptual_question(topic, difficulty):
    """Generate conceptual questions"""
    concept_templates = {
        'easy': f"Which statement best describes {topic}?",
        'medium': f"What is the most significant aspect of {topic}?",
        'hard': f"Which principle is most fundamental to understanding {topic}?"
    }
    
    question = concept_templates.get(difficulty, concept_templates['medium'])
    options = generate_contextual_options(topic, difficulty)
    
    return {
        "question": question,
        "options": options,
        "correctOption": 0,
        "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
        "difficulty": difficulty
    }

def generate_contextual_options(topic, difficulty):
    """Generate more realistic options based on topic"""
    base_options = [
        f"Core principle of {topic}",
        f"Related concept in the field",
        f"Common misconception about {topic}",
        f"Advanced application of {topic}"
    ]
    
    if difficulty == 'easy':
        return [
            f"Basic understanding of {topic}",
            f"Incorrect interpretation",
            f"Unrelated concept",
            f"Partial knowledge"
        ]
    elif difficulty == 'hard':
        return [
            f"Advanced theoretical framework of {topic}",
            f"Complex but incorrect interpretation",
            f"Sophisticated but wrong approach",
            f"Partially correct but incomplete understanding"
        ]
    
    return base_options

def calculate_time_limit(num_questions, difficulty):
    """Calculate appropriate time limit for quiz"""
    base_time_per_question = {
        'easy': 30,      # 30 seconds per question
        'medium': 45,    # 45 seconds per question
        'hard': 60       # 60 seconds per question
    }
    
    time_per_question = base_time_per_question.get(difficulty, 45)
    total_time = num_questions * time_per_question
    
    return total_time  # Return in seconds

def generate_explanation(question, is_correct):
    """Simple explanation for backward compatibility"""
    if is_correct:
        return "Excellent! You got this right."
    else:
        return "Not quite right. Check the source link to learn more."

def generate_study_resources(topic):
    """Generate study resources for the topic"""
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
        quiz_type = data.get('quiz_type', 'mixed')  # New parameter
        
        print(f"Generating quiz: {topic}, {num_questions} questions, {difficulty}")
        
        # Use enhanced question generation
        questions = generate_advanced_quiz_questions(topic, num_questions, difficulty)
        
        # Store quiz with additional metadata
        quiz_id = str(len(quizzes) + 1)
        quiz_data = {
            'id': quiz_id,
            'title': f"{topic} Quiz - {difficulty.title()} Level",
            'topic': topic,
            'num_questions': num_questions,
            'difficulty': difficulty,
            'quiz_type': quiz_type,
            'questions': questions,
            'created_by': current_user['id'],
            'created_by_name': current_user['name'],
            'created_at': datetime.now().isoformat(),
            'is_active': True,
            'time_limit': calculate_time_limit(num_questions, difficulty)
        }
        quizzes[quiz_id] = quiz_data
        
        print(f"Quiz created successfully: ID {quiz_id}")
        
        return jsonify({
            "quiz_id": quiz_id,
            "title": quiz_data['title'],
            "questions": questions,
            "total_questions": len(questions),
            "topic": topic,
            "difficulty": difficulty,
            "time_limit": quiz_data['time_limit'],
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

@app.route('/api/quiz/<quiz_id>', methods=['GET'])
@token_required
def get_quiz(current_user, quiz_id):
    """Get a specific quiz by ID"""
    quiz = quizzes.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    # Students can only see active quizzes
    if current_user['role'] == 'student' and not quiz.get('is_active', True):
        return jsonify({'error': 'Quiz not available'}), 403
    
    # Don't send correct answers to students before they submit
    if current_user['role'] == 'student':
        questions_for_student = []
        for q in quiz['questions']:
            student_question = {k: v for k, v in q.items() if k != 'correctOption'}
            questions_for_student.append(student_question)
        quiz['questions'] = questions_for_student
    
    return jsonify({'quiz': quiz})

@app.route('/api/quiz/<quiz_id>', methods=['PUT'])
@token_required
def update_quiz(current_user, quiz_id):
    """Update quiz (lecturer only)"""
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    quiz = quizzes.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    if quiz['created_by'] != current_user['id']:
        return jsonify({'error': 'Not authorized to edit this quiz'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    updateable_fields = ['title', 'is_active', 'time_limit']
    for field in updateable_fields:
        if field in data:
            quiz[field] = data[field]
    
    quiz['updated_at'] = datetime.now().isoformat()
    
    return jsonify({'message': 'Quiz updated successfully', 'quiz': quiz})

@app.route('/api/quiz/<quiz_id>', methods=['DELETE'])
@token_required
def delete_quiz(current_user, quiz_id):
    """Delete quiz (lecturer only)"""
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    quiz = quizzes.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    if quiz['created_by'] != current_user['id']:
        return jsonify({'error': 'Not authorized to delete this quiz'}), 403
    
    del quizzes[quiz_id]
    
    return jsonify({'message': 'Quiz deleted successfully'})

@app.route('/api/quiz/<quiz_id>/submit', methods=['POST'])
@token_required
def submit_quiz(current_user, quiz_id):
    """Submit quiz answers"""
    quiz = quizzes.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    data = request.get_json()
    user_answers = data.get('answers', [])
    time_taken = data.get('time_taken', 0)
    
    # Calculate score using existing logic
    questions = quiz['questions']
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
            "explanation": generate_detailed_explanation(question, is_correct, user_answer)
        }
        detailed_results.append(result)
    
    score_percentage = (correct_answers / total_questions) * 100
    
    # Enhanced performance feedback
    performance_data = calculate_performance_metrics(score_percentage, time_taken, quiz.get('time_limit', 300))
    
    # Store detailed grade record
    grade_id = str(len(grades) + 1)
    grade_record = {
        'id': grade_id,
        'quiz_id': quiz_id,
        'quiz_title': quiz.get('title', quiz['topic']),
        'user_id': current_user['id'],
        'user_name': current_user['name'],
        'user_email': current_user['email'],
        'topic': quiz['topic'],
        'difficulty': quiz['difficulty'],
        'score': correct_answers,
        'total': total_questions,
        'percentage': round(score_percentage, 1),
        'time_taken': time_taken,
        'time_limit': quiz.get('time_limit', 300),
        'completed_at': datetime.now().isoformat(),
        'results': detailed_results,
        'performance_data': performance_data
    }
    grades[grade_id] = grade_record
    
    return jsonify({
        "quiz_id": quiz_id,
        "quiz_title": quiz.get('title', quiz['topic']),
        "score": {
            "correct": correct_answers,
            "total": total_questions,
            "percentage": round(score_percentage, 1),
            "performance": performance_data['level'],
            "time_taken": time_taken,
            "time_efficiency": performance_data['time_efficiency']
        },
        "results": detailed_results,
        "study_resources": generate_study_resources(quiz['topic']),
        "grade_id": grade_id
    })

# Move analytics endpoints before the main execution block
@app.route('/api/lecturer/analytics', methods=['GET'])
@token_required
def get_analytics(current_user):
    """Get comprehensive analytics for lecturer"""
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    # Calculate various statistics
    lecturer_quizzes = [q for q in quizzes.values() if q.get('created_by') == current_user['id']]
    lecturer_grades = [g for g in grades.values() if any(q['id'] == g.get('quiz_id') for q in lecturer_quizzes)]
    
    analytics = {
        'overview': {
            'total_quizzes': len(lecturer_quizzes),
            'total_students': len(set(g['user_id'] for g in lecturer_grades)),
            'total_attempts': len(lecturer_grades),
            'average_score': round(sum(g['percentage'] for g in lecturer_grades) / len(lecturer_grades), 1) if lecturer_grades else 0
        },
        'quiz_performance': [],
        'student_performance': [],
        'difficulty_analysis': calculate_difficulty_analysis(lecturer_grades),
        'topic_popularity': calculate_topic_popularity(lecturer_quizzes, lecturer_grades),
        'recent_activity': get_recent_activity(lecturer_grades)
    }
    
    # Quiz performance breakdown
    for quiz in lecturer_quizzes:
        quiz_grades = [g for g in lecturer_grades if g.get('quiz_id') == quiz['id']]
        if quiz_grades:
            avg_score = sum(g['percentage'] for g in quiz_grades) / len(quiz_grades)
            analytics['quiz_performance'].append({
                'quiz_id': quiz['id'],
                'title': quiz.get('title', quiz['topic']),
                'attempts': len(quiz_grades),
                'average_score': round(avg_score, 1),
                'highest_score': max(g['percentage'] for g in quiz_grades),
                'lowest_score': min(g['percentage'] for g in quiz_grades)
            })
    
    # Student performance summary
    student_stats = {}
    for grade in lecturer_grades:
        student_id = grade['user_id']
        if student_id not in student_stats:
            student_stats[student_id] = {
                'name': grade['user_name'],
                'email': grade['user_email'],
                'attempts': 0,
                'total_score': 0,
                'quizzes_taken': []
            }
        
        student_stats[student_id]['attempts'] += 1
        student_stats[student_id]['total_score'] += grade['percentage']
        student_stats[student_id]['quizzes_taken'].append({
            'quiz_title': grade.get('quiz_title', grade['topic']),
            'score': grade['percentage'],
            'date': grade['completed_at']
        })
    
    for student_id, stats in student_stats.items():
        stats['average_score'] = round(stats['total_score'] / stats['attempts'], 1)
        analytics['student_performance'].append(stats)
    
    return jsonify({'analytics': analytics})

@app.route('/api/lecturer/quiz/<quiz_id>/analytics', methods=['GET'])
@token_required
def get_quiz_analytics(current_user, quiz_id):
    """Get detailed analytics for a specific quiz"""
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    quiz = quizzes.get(quiz_id)
    if not quiz or quiz['created_by'] != current_user['id']:
        return jsonify({'error': 'Quiz not found or access denied'}), 404
    
    quiz_grades = [g for g in grades.values() if g.get('quiz_id') == quiz_id]
    
    if not quiz_grades:
        return jsonify({'message': 'No attempts yet', 'analytics': None})
    
    # Detailed question analysis
    question_analysis = []
    for i, question in enumerate(quiz['questions']):
        correct_count = 0
        total_attempts = len(quiz_grades)
        
        for grade in quiz_grades:
            if i < len(grade['results']) and grade['results'][i]['is_correct']:
                correct_count += 1
        
        success_rate = (correct_count / total_attempts * 100) if total_attempts > 0 else 0
        
        question_analysis.append({
            'question_id': i + 1,
            'question': question['question'],
            'success_rate': round(success_rate, 1),
            'difficulty': question.get('difficulty', 'medium'),
            'correct_attempts': correct_count,
            'total_attempts': total_attempts
        })
    
    analytics = {
        'quiz_info': {
            'title': quiz.get('title', quiz['topic']),
            'topic': quiz['topic'],
            'difficulty': quiz['difficulty'],
            'total_questions': len(quiz['questions'])
        },
        'performance_summary': {
            'total_attempts': len(quiz_grades),
            'average_score': round(sum(g['percentage'] for g in quiz_grades) / len(quiz_grades), 1),
            'highest_score': max(g['percentage'] for g in quiz_grades),
            'lowest_score': min(g['percentage'] for g in quiz_grades),
            'pass_rate': round(len([g for g in quiz_grades if g['percentage'] >= 70]) / len(quiz_grades) * 100, 1)
        },
        'question_analysis': question_analysis,
        'score_distribution': calculate_score_distribution(quiz_grades),
        'time_analysis': calculate_time_analysis(quiz_grades, quiz.get('time_limit', 0))
    }
    
    return jsonify({'analytics': analytics})

def calculate_score_distribution(grades):
    """Calculate score distribution"""
    distribution = {
        'A (90-100%)': 0,
        'B (80-89%)': 0,
        'C (70-79%)': 0,
        'D (60-69%)': 0,
        'F (0-59%)': 0
    }
    
    for grade in grades:
        score = grade['percentage']
        if score >= 90:
            distribution['A (90-100%)'] += 1
        elif score >= 80:
            distribution['B (80-89%)'] += 1
        elif score >= 70:
            distribution['C (70-79%)'] += 1
        elif score >= 60:
            distribution['D (60-69%)'] += 1
        else:
            distribution['F (0-59%)'] += 1
    
    return distribution

def calculate_time_analysis(grades, time_limit):
    """Analyze time usage patterns"""
    if not grades or time_limit <= 0:
        return None
    
    times = [g.get('time_taken', 0) for g in grades if g.get('time_taken', 0) > 0]
    
    if not times:
        return None
    
    return {
        'average_time': round(sum(times) / len(times), 1),
        'fastest_time': min(times),
        'slowest_time': max(times),
        'time_limit': time_limit,
        'average_time_usage': round((sum(times) / len(times)) / time_limit * 100, 1)
    }

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 400
        
        # For now, we'll decode the JWT token manually since google-auth might not be installed
        # In production, use proper Google token verification
        try:
            import json
            import base64
            
            # Decode JWT payload (unsafe in production - use google-auth library)
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            user_info = json.loads(decoded)
            
            email = user_info.get('email')
            name = user_info.get('name', email.split('@')[0])
            picture = user_info.get('picture', '')
            
            if not email:
                return jsonify({'error': 'Invalid Google token'}), 401
            
        except Exception as e:
            print(f"Token decode error: {e}")
            return jsonify({'error': 'Invalid Google token'}), 401
        
        # Check if user exists or create new user
        user = users.get(email)
        if not user:
            # Create new user from Google account
            user_id = str(len(users) + 1)
            user = {
                'id': user_id,
                'email': email,
                'name': name,
                'role': 'student',  # Default role
                'picture': picture,
                'auth_provider': 'google',
                'created_at': datetime.now().isoformat()
            }
            users[email] = user
            print(f"New Google user created: {email}")
        else:
            # Update existing user
            user['picture'] = picture
            user['auth_provider'] = 'google'
            print(f"Existing user logged in with Google: {email}")
        
        # Generate JWT token
        jwt_token = jwt.encode({
            'user_id': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256')
        
        # Return user data
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return jsonify({
            "message": "Google authentication successful",
            "user": user_data,
            "token": jwt_token
        }), 200
        
    except Exception as e:
        print(f"Google auth error: {e}")
        return jsonify({'error': 'Google authentication failed'}), 500

@app.route('/api/quiz/<int:quiz_id>/save', methods=['PUT'])
@jwt_required()
def save_quiz(quiz_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Find the quiz
        quiz = Quiz.query.filter_by(id=quiz_id, creator_id=current_user_id).first()
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Update quiz data
        if 'title' in data:
            quiz.title = data['title']
        if 'questions' in data:
            quiz.questions = data['questions']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz updated successfully',
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'subject': quiz.subject,
                'difficulty': quiz.difficulty,
                'questions': quiz.questions
            }
        })
        
    except Exception as e:
        print(f"Save quiz error: {str(e)}")
        return jsonify({'error': 'Failed to save quiz'}), 500

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
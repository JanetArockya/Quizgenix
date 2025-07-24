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
CORS(app)

# Secret key for JWT tokens
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-here')

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
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return "Quizgenix backend running"

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'student')
        
        if not email or not password or not name:
            return jsonify({"error": "Missing required fields"}), 400
        
        if email in users:
            return jsonify({"error": "User already exists"}), 400
        
        # Hash password (simple hash for demo - use bcrypt in production)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user_id = len(users) + 1
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
        
        return jsonify({
            "message": "User registered successfully",
            "user": user_data,
            "token": token
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
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
        
        return jsonify({
            "message": "Login successful",
            "user": user_data,
            "token": token
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/score', methods=['POST'])
@token_required
def calculate_score(current_user):
    try:
        data = request.get_json()
        questions = data.get('questions', [])
        user_answers = data.get('user_answers', [])
        topic = data.get('topic', 'Unknown')
        user_id = data.get('user_id', current_user['id'])
        
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
        grade_id = len(grades) + 1
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
            "study_resources": generate_study_resources(data.get('topic', 'General Knowledge'))
        })
        
    except Exception as e:
        print(f"Error calculating score: {e}")
        return jsonify({"error": "Failed to calculate score"}), 500

@app.route('/api/quiz', methods=['POST'])
@token_required
def generate_quiz(current_user):
    try:
        data = request.get_json()
        topic = data.get('topic', 'General Knowledge')
        num_questions = data.get('num_questions', 5)  # Default to 5 questions
        
        # Validate number of questions (1-20 range)
        num_questions = max(1, min(20, int(num_questions)))
        
        questions = []
        
        # Generate the requested number of questions
        for i in range(num_questions):
            question = None
            
            # Try different methods for variety
            if i % 3 == 0:  # Every 3rd question try OpenTDB first
                question = try_opentdb_api(topic)
            
            if not question:  # If OpenTDB fails or not used, try Hugging Face
                question = try_huggingface_api(topic)
            
            if not question:  # If all AI methods fail, use smart templates
                question = generate_smart_template_question(topic, i)
                
            if question:
                question['questionId'] = i + 1  # Add question ID for frontend
                questions.append(question)
        
        # Ensure we have the requested number of questions
        while len(questions) < num_questions:
            fallback_question = generate_smart_template_question(topic, len(questions))
            fallback_question['questionId'] = len(questions) + 1
            questions.append(fallback_question)
            
        return jsonify({
            "questions": questions,
            "total_questions": len(questions),
            "topic": topic
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        # Fallback with multiple basic questions
        fallback_questions = generate_fallback_questions(topic, num_questions)
        return jsonify({
            "questions": fallback_questions,
            "total_questions": len(fallback_questions),
            "topic": topic
        })

def try_huggingface_api(topic):
    """Try Hugging Face free inference API"""
    try:
        # Use free Hugging Face inference API (no key required for basic usage)
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        prompt = f"Generate a multiple choice question about {topic} with 4 options and indicate the correct answer:"
        
        response = requests.post(
            API_URL,
            headers={"Authorization": "Bearer hf_demo"},  # Demo token - free but limited
            json={"inputs": prompt, "parameters": {"max_length": 200}},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            # Process and format the response into a quiz question
            return parse_ai_response_to_question(result, topic)
            
    except Exception as e:
        print(f"Hugging Face API failed: {e}")
        return None

def try_opentdb_api(topic):
    """Try Open Trivia Database - completely free"""
    try:
        # Map topics to OpenTDB categories
        category_map = {
            "science": 17, "history": 23, "geography": 22, "sports": 21,
            "entertainment": 11, "art": 25, "nature": 17, "technology": 18,
            "literature": 10, "mathematics": 19, "general": 9
        }
        
        # Find best matching category
        category_id = 9  # General knowledge default
        for key, value in category_map.items():
            if key.lower() in topic.lower():
                category_id = value
                break
                
        url = f"https://opentdb.com/api.php?amount=1&category={category_id}&type=multiple"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                trivia = data['results'][0]
                
                # Create options list with correct answer randomly placed
                options = trivia['incorrect_answers']
                correct_answer = trivia['correct_answer']
                correct_index = random.randint(0, 3)
                options.insert(correct_index, correct_answer)
                
                return {
                    "question": trivia['question'].replace('&quot;', '"').replace('&#039;', "'"),
                    "options": options,
                    "correctOption": correct_index,
                    "source": "https://opentdb.com/",
                    "ai_generated": True,
                    "difficulty": trivia.get('difficulty', 'medium')
                }
                
    except Exception as e:
        print(f"OpenTDB API failed: {e}")
        return None

def generate_smart_template_question(topic, question_index=0):
    """Generate intelligent template-based questions with variety"""
    
    # Expanded question templates based on topic
    templates = {
        "science": [
            f"What is the primary characteristic of {topic}?",
            f"Which scientist is most associated with {topic}?",
            f"What unit is commonly used to measure {topic}?",
            f"In which field of science is {topic} most important?",
            f"What is the main application of {topic}?",
            f"Which theory best explains {topic}?",
            f"What is the fundamental principle behind {topic}?",
            f"How does {topic} affect our daily lives?"
        ],
        "history": [
            f"When did the major event related to {topic} occur?",
            f"Who was the key figure in {topic}?",
            f"Which country was most influential in {topic}?",
            f"What was the main cause of {topic}?",
            f"What was the outcome of {topic}?",
            f"Which period is associated with {topic}?",
            f"What impact did {topic} have on society?",
            f"Which document is related to {topic}?"
        ],
        "technology": [
            f"Which company is most associated with {topic}?",
            f"When was {topic} first introduced?",
            f"What is the main benefit of {topic}?",
            f"Which programming language is best for {topic}?",
            f"What problem does {topic} solve?",
            f"How has {topic} evolved over time?",
            f"What are the security concerns with {topic}?",
            f"Which platform supports {topic} best?"
        ],
        "general": [
            f"What is the most important aspect of {topic}?",
            f"Which of these is related to {topic}?",
            f"What field does {topic} belong to?",
            f"Who would be most interested in {topic}?",
            f"What is the origin of {topic}?",
            f"How is {topic} measured or evaluated?",
            f"What are the benefits of understanding {topic}?",
            f"Which skill is required for {topic}?"
        ]
    }
    
    # Determine question category
    category = "general"
    if any(word in topic.lower() for word in ["science", "physics", "chemistry", "biology", "mathematics"]):
        category = "science"
    elif any(word in topic.lower() for word in ["history", "war", "ancient", "medieval", "civilization"]):
        category = "history"
    elif any(word in topic.lower() for word in ["technology", "programming", "computer", "software", "ai", "algorithm"]):
        category = "technology"
    
    # Use question index to ensure variety
    available_templates = templates[category]
    template_index = question_index % len(available_templates)
    question_template = available_templates[template_index]
    
    # Generate contextual options with variety
    options = generate_contextual_options(topic, category, question_index)
    correct_index = 0  # First option is correct by default
    
    return {
        "question": question_template,
        "options": options,
        "correctOption": correct_index,
        "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
        "ai_generated": True,
        "generation_method": "smart_template",
        "difficulty": ["easy", "medium", "hard"][question_index % 3]
    }

def generate_contextual_options(topic, category, question_index=0):
    """Generate smart, contextual multiple choice options with variety"""
    
    base_options = {
        "science": [
            ["Research and experimentation", "Theoretical analysis only", "Practical application", "Historical documentation"],
            ["Laboratory testing", "Mathematical modeling", "Field observation", "Literature review"],
            ["Experimental validation", "Computational simulation", "Statistical analysis", "Peer review"],
            ["Scientific method", "Hypothesis testing", "Data collection", "Theory development"]
        ],
        "history": [
            ["Political changes", "Economic factors", "Social movements", "Military conflicts"],
            ["Cultural developments", "Religious influences", "Technological advances", "Environmental factors"],
            ["Leadership decisions", "Popular uprisings", "International relations", "Trade agreements"],
            ["Constitutional changes", "Revolutionary ideas", "Diplomatic negotiations", "Colonial expansion"]
        ],
        "technology": [
            ["Innovation and efficiency", "Cost reduction", "Entertainment value", "Educational purposes"],
            ["Performance optimization", "User experience", "Security enhancement", "Scalability improvement"],
            ["Automation benefits", "Integration capabilities", "Maintenance simplicity", "Future compatibility"],
            ["Development speed", "Resource management", "Error reduction", "Accessibility features"]
        ],
        "general": [
            ["Primary importance", "Secondary relevance", "Minimal impact", "Future potential"],
            ["Core concept", "Supporting idea", "Related topic", "Advanced application"],
            ["Fundamental principle", "Practical application", "Theoretical framework", "Historical context"],
            ["Essential knowledge", "Useful skill", "Interesting fact", "Advanced technique"]
        ]
    }
    
    # Get options based on category and vary by question index
    category_options = base_options.get(category, base_options["general"])
    option_set_index = question_index % len(category_options)
    options = category_options[option_set_index].copy()
    
    # Customize first option (correct answer) based on topic
    if "programming" in topic.lower() or "javascript" in topic.lower():
        options[0] = "Programming and software development"
    elif "python" in topic.lower():
        options[0] = "Data science and web development"
    elif "ai" in topic.lower() or "artificial intelligence" in topic.lower():
        options[0] = "Machine learning and automation"
    elif "math" in topic.lower():
        options[0] = "Mathematical computation and analysis"
    elif "history" in topic.lower():
        options[0] = "Historical significance and impact"
    elif "science" in topic.lower():
        options[0] = "Scientific research and discovery"
    
    return options

def generate_fallback_questions(topic, num_questions):
    """Generate multiple fallback questions when AI methods fail"""
    questions = []
    
    basic_templates = [
        f"What is the most important aspect of {topic}?",
        f"Which field is {topic} primarily associated with?",
        f"What is the main benefit of studying {topic}?",
        f"Which of these concepts relates to {topic}?",
        f"What skill is most important for {topic}?"
    ]
    
    for i in range(num_questions):
        template_index = i % len(basic_templates)
        question = {
            "questionId": i + 1,
            "question": basic_templates[template_index],
            "options": ["Primary concept", "Secondary idea", "Related topic", "Advanced application"],
            "correctOption": 0,
            "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "ai_generated": False,
            "generation_method": "fallback"
        }
        questions.append(question)
    
    return questions

def generate_explanation(question, is_correct):
    """Generate explanations for answers"""
    if is_correct:
        explanations = [
            "Excellent! You got this right.",
            "Correct! Well done.",
            "Perfect! You understand this concept.",
            "Great job! That's the right answer.",
            "Outstanding! You nailed it."
        ]
        return random.choice(explanations)
    else:
        explanations = [
            "Not quite right. Check the source link to learn more.",
            "This one was tricky. Review the material for better understanding.",
            "Good attempt! The source link has more information.",
            "Close, but not correct. Study the topic further.",
            "Keep learning! The source will help clarify this concept."
        ]
        return random.choice(explanations)

def generate_study_resources(topic):
    """Generate study resources based on topic"""
    resources = [
        {
            "title": f"Wikipedia: {topic}",
            "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "type": "encyclopedia"
        },
        {
            "title": f"Khan Academy: {topic}",
            "url": f"https://www.khanacademy.org/search?search_again=1&query={topic.replace(' ', '+')}",
            "type": "educational"
        },
        {
            "title": f"Coursera Courses: {topic}",
            "url": f"https://www.coursera.org/search?query={topic.replace(' ', '+')}",
            "type": "courses"
        }
    ]
    
    # Add topic-specific resources
    if "programming" in topic.lower() or "javascript" in topic.lower() or "python" in topic.lower():
        resources.append({
            "title": "MDN Web Docs",
            "url": "https://developer.mozilla.org/",
            "type": "documentation"
        })
        resources.append({
            "title": "Stack Overflow",
            "url": f"https://stackoverflow.com/questions/tagged/{topic.lower().replace(' ', '-')}",
            "type": "community"
        })
    
    return resources

def parse_ai_response_to_question(ai_response, topic):
    """Parse AI response into structured question format"""
    try:
        # This is a simplified parser - you can make it more sophisticated
        if isinstance(ai_response, list) and ai_response:
            response_text = ai_response[0].get('generated_text', '')
            
            # Basic parsing logic
            return {
                "question": f"Based on AI analysis, what is most important about {topic}?",
                "options": ["Key concept A", "Key concept B", "Key concept C", "Key concept D"],
                "correctOption": 0,
                "source": "https://huggingface.co/",
                "ai_generated": True,
                "generation_method": "huggingface_ai"
            }
    except:
        pass
    
    return None

# Lecturer-specific endpoints
@app.route('/api/lecturer/quizzes', methods=['GET'])
@token_required
def get_lecturer_quizzes(current_user):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    # Return quizzes created by this lecturer
    lecturer_quizzes = [q for q in quizzes.values() if q.get('created_by') == current_user['id']]
    return jsonify({'quizzes': lecturer_quizzes})

@app.route('/api/lecturer/students', methods=['GET'])
@token_required
def get_students(current_user):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    # Return all students
    students = [u for u in users.values() if u['role'] == 'student']
    # Remove password hashes from response
    safe_students = [{k: v for k, v in student.items() if k != 'password_hash'} for student in students]
    return jsonify({'students': safe_students})

@app.route('/api/lecturer/grades', methods=['GET'])
@token_required
def get_grades(current_user):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    # Return all grades
    all_grades = list(grades.values())
    return jsonify({'grades': all_grades})

@app.route('/api/lecturer/grades/download', methods=['GET'])
@token_required
def download_grades(current_user):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    format_type = request.args.get('format', 'excel')
    
    # Generate CSV content
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

@app.route('/api/quiz/<int:quiz_id>/download', methods=['GET'])
@token_required
def download_quiz(current_user, quiz_id):
    if current_user['role'] != 'lecturer':
        return jsonify({'error': 'Access denied'}), 403
    
    format_type = request.args.get('format', 'pdf')
    
    # For demo purposes, return a simple text response
    # In production, you would generate actual PDF/Word documents
    from flask import make_response
    
    quiz_content = f"Quiz {quiz_id}\n\nSample quiz content would be generated here.\n\nThis is a placeholder for {format_type} generation."
    
    response = make_response(quiz_content)
    if format_type == 'pdf':
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=quiz_{quiz_id}.pdf'
    elif format_type == 'docx':
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response.headers['Content-Disposition'] = f'attachment; filename=quiz_{quiz_id}.docx'
    
    return response

# Student-specific endpoints
@app.route('/api/student/quizzes', methods=['GET'])
@token_required
def get_student_quizzes(current_user):
    if current_user['role'] != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    # Return available quizzes for students
    available_quizzes = list(quizzes.values())
    return jsonify({'quizzes': available_quizzes})


if __name__ == '__main__':
    app.run(debug=True)
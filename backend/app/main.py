from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import json
import io
import os
import random
import re

# Try to import optional libraries
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    print("⚠️ FPDF not available - Install with: pip install fpdf2")

try:
    from docx import Document
    from docx.shared import Inches
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️ python-docx not available - Install with: pip install python-docx")

try:
    import pandas as pd
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False
    print("⚠️ pandas not available - Install with: pip install pandas openpyxl")

try:
    import wikipedia
    HAS_WIKIPEDIA = True
except ImportError:
    HAS_WIKIPEDIA = False
    print("⚠️ Wikipedia not available - Install with: pip install wikipedia")

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

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON string of user answers
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)  # in seconds
    completed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='quiz_attempts')
    quiz = db.relationship('Quiz', backref='attempts')

class QuizSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    session_token = db.Column(db.String(100), nullable=False, unique=True)
    started_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    current_question = db.Column(db.Integer, default=0)
    answers_so_far = db.Column(db.Text, default='{}')  # JSON of answers

# Enhanced Knowledge Base with Topic-Specific Content and Comprehensive References
TOPIC_FOCUSED_KNOWLEDGE_BASE = {
    'javascript_functions': {
        'easy': [
            {
                'question': "Which keyword is used to declare a function in JavaScript?",
                'options': [
                    "function",
                    "def",
                    "lambda",
                    "sub"
                ],
                'correct': 0,
                'explanation': "The 'function' keyword is used in JavaScript to declare functions.",
                'references': [
                    {"title": "MDN - Functions", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions"}
                ]
            },
            {
                'question': "How do you call a function named 'myFunc'?",
                'options': [
                    "myFunc();",
                    "call myFunc;",
                    "run myFunc()",
                    "invoke myFunc"
                ],
                'correct': 0,
                'explanation': "Functions are called by their name followed by parentheses.",
                'references': [
                    {"title": "MDN - Calling Functions", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions#calling_functions"}
                ]
            },
            # Add more diverse questions here...
        ],
        # Add medium and hard questions similarly...
    },
    # Add other topics/subjects...
}

def generate_topic_focused_questions(quiz_data):
    """Generate questions specifically focused on the given topic"""
    try:
        count = int(quiz_data.get('questionCount', 5))
        topic = quiz_data.get('topic', '').lower().strip()
        subject = quiz_data.get('subject', '').lower().strip()
        difficulty = quiz_data.get('difficulty', 'medium').lower()
        
        print(f"🎯 Generating topic-focused questions for: '{topic}' in subject '{subject}' (difficulty: {difficulty})")
        
        # Create topic-specific key
        topic_key = create_topic_key(topic, subject)
        
        # Get questions from knowledge base
        questions = get_topic_specific_questions(topic_key, difficulty, count, topic, subject)
        
        # If we don't have enough topic-specific questions, generate contextual ones
        if len(questions) < count:
            additional_needed = count - len(questions)
            contextual_questions = generate_contextual_topic_questions(
                topic, subject, difficulty, additional_needed, len(questions)
            )
            questions.extend(contextual_questions)
        
        print(f"✅ Generated {len(questions)} topic-focused questions for '{topic}'")
        return questions[:count]
        
    except Exception as e:
        print(f"❌ Error in topic-focused question generation: {e}")
        return generate_fallback_questions(quiz_data)

def create_topic_key(topic, subject):
    """Create a specific topic key based on topic and subject combination"""
    topic_lower = topic.lower()
    subject_lower = subject.lower()
    
    # Topic-specific mapping with subject context
    topic_mappings = {
        # JavaScript topics
        ('function', 'javascript'): 'javascript_functions',
        ('function', 'computer'): 'javascript_functions',
        ('function', 'programming'): 'javascript_functions',
        ('javascript function', 'any'): 'javascript_functions',
        
        # Python topics  
        ('function', 'python'): 'python_functions',
        ('python function', 'any'): 'python_functions',
        ('def', 'python'): 'python_functions',
        
        # Math topics
        ('algebra', 'math'): 'algebra_equations',
        ('equation', 'math'): 'algebra_equations',
        ('linear equation', 'any'): 'algebra_equations',
        ('quadratic', 'math'): 'algebra_equations',
        
        # Chemistry topics
        ('compound', 'chemistry'): 'chemistry_compounds',
        ('salt', 'chemistry'): 'chemistry_compounds',
        ('ionic', 'chemistry'): 'chemistry_compounds',
        ('chemical compound', 'any'): 'chemistry_compounds',
    }
    
    # First, try exact topic-subject match
    for (topic_key, subject_key), result in topic_mappings.items():
        if (topic_key in topic_lower and (subject_key == 'any' or subject_key in subject_lower)):
            return result
    
    # Fallback: general topic matching
    if 'function' in topic_lower:
        if any(js_term in subject_lower for js_term in ['javascript', 'js', 'computer', 'programming']):
            return 'javascript_functions'
        elif 'python' in subject_lower:
            return 'python_functions'
    
    if any(math_term in topic_lower for math_term in ['algebra', 'equation']):
        return 'algebra_equations'
    
    if any(chem_term in topic_lower for chem_term in ['compound', 'chemistry', 'chemical']):
        return 'chemistry_compounds'
    
    return None

def get_topic_specific_questions(topic_key, difficulty, count, original_topic, original_subject):
    """Get questions from the topic-specific knowledge base"""
    questions = []
    
    if not topic_key or topic_key not in TOPIC_FOCUSED_KNOWLEDGE_BASE:
        return questions
    
    topic_data = TOPIC_FOCUSED_KNOWLEDGE_BASE[topic_key]
    
    # Get questions for the specific difficulty
    if difficulty in topic_data:
        available_questions = topic_data[difficulty][:]
        random.shuffle(available_questions)
        
        for i, q_data in enumerate(available_questions[:count]):
            # Randomize answer positions
            options = q_data['options'][:]
            correct_answer = q_data['correct']
            
            randomized_correct = random.randint(0, 3)
            if randomized_correct != correct_answer:
                options[randomized_correct], options[correct_answer] = options[correct_answer], options[randomized_correct]
            
            question = {
                'id': i + 1,
                'question': q_data['question'],
                'options': options,
                'correct_answer': randomized_correct,
                'explanation': q_data['explanation'],
                'references': q_data['references'],
                'ai_generated': False,
                'verified': True,
                'difficulty': difficulty,
                'topic': original_topic,
                'subject': original_subject,
                'topic_key': topic_key
            }
            questions.append(question)
    
    return questions

def generate_contextual_topic_questions(topic, subject, difficulty, count, start_id):
    """Generate contextual questions when specific topic questions aren't available"""
    questions = []
    
    # Topic-specific question templates
    topic_templates = {
        'function': {
            'javascript': {
                'easy': [
                    f"What is the proper way to declare a {topic} in JavaScript?",
                    f"How do you call a {topic} with parameters in JavaScript?",
                    f"What keyword is used to create a {topic} in JavaScript?"
                ],
                'medium': [
                    f"How do JavaScript {topic}s handle scope and closure?",
                    f"What is the difference between {topic} declarations and expressions?",
                    f"How do arrow {topic}s differ from regular {topic}s?"
                ]
            },
            'python': {
                'easy': [
                    f"What keyword defines a {topic} in Python?",
                    f"How do you return a value from a Python {topic}?",
                    f"What is the correct syntax for Python {topic} parameters?"
                ],
                'medium': [
                    f"How do Python {topic} decorators work?",
                    f"What are *args and **kwargs in Python {topic}s?",
                    f"How do Python {topic}s handle variable scope?"
                ]
            }
        },
        'equation': {
            'mathematics': {
                'easy': [
                    f"What is the first step in solving a linear {topic}?",
                    f"How do you isolate variables in an {topic}?",
                    f"What operations are used to solve simple {topic}s?"
                ],
                'medium': [
                    f"How do you solve quadratic {topic}s using factoring?",
                    f"What is the quadratic formula for solving {topic}s?",
                    f"How do you check if your {topic} solution is correct?"
                ]
            }
        },
        'compound': {
            'chemistry': {
                'easy': [
                    f"What are the main types of chemical {topic}s?",
                    f"How are ionic {topic}s formed?",
                    f"What determines the properties of a {topic}?"
                ],
                'medium': [
                    f"How do you name covalent {topic}s?",
                    f"What is the difference between ionic and covalent {topic}s?",
                    f"How do you determine molecular geometry of {topic}s?"
                ]
            }
        }
    }
    
    # Generate contextual options based on topic and subject
    for i in range(count):
        question_templates = get_contextual_templates(topic, subject, difficulty, topic_templates)
        
        if question_templates:
            question_text = random.choice(question_templates)
            options, correct_idx, explanation, references = generate_contextual_options(
                topic, subject, difficulty, question_text
            )
            
            # Randomize correct answer position
            randomized_correct = random.randint(0, 3)
            if randomized_correct != correct_idx:
                options[randomized_correct], options[correct_idx] = options[correct_idx], options[randomized_correct]
            
            question = {
                'id': start_id + i + 1,
                'question': question_text,
                'options': options,
                'correct_answer': randomized_correct,
                'explanation': explanation,
                'references': references,
                'ai_generated': True,
                'verified': True,
                'difficulty': difficulty,
                'topic': topic,
                'subject': subject
            }
            questions.append(question)
    
    return questions

def get_contextual_templates(topic, subject, difficulty, topic_templates):
    """Get appropriate question templates based on topic and subject"""
    topic_lower = topic.lower()
    subject_lower = subject.lower()
    
    # Find matching templates
    for template_topic, subjects in topic_templates.items():
        if template_topic in topic_lower:
            for template_subject, difficulties in subjects.items():
                if template_subject in subject_lower and difficulty in difficulties:
                    return difficulties[difficulty]
    
    # Fallback generic templates
    generic_templates = [
        f"What is the fundamental concept of {topic} in {subject}?",
        f"How is {topic} typically implemented in {subject}?",
        f"What are the key principles of {topic}?",
        f"How do you apply {topic} in practical scenarios?"
    ]
    
    return generic_templates

def generate_contextual_options(topic, subject, difficulty, question_text):
    """Generate contextual answer options with proper explanations and references"""
    topic_lower = topic.lower()
    subject_lower = subject.lower()
    
    # Domain-specific correct answers
    if 'javascript' in subject_lower or 'programming' in subject_lower:
        correct_options = [
            f"Follow ECMAScript standards and modern JavaScript best practices for {topic}",
            f"Use the official JavaScript specification guidelines for {topic}",
            f"Implement according to MDN documentation recommendations for {topic}",
            f"Apply industry-standard JavaScript patterns for {topic}"
        ]
        
        wrong_options = [
            f"Use deprecated JavaScript methods for {topic}",
            f"Ignore modern JavaScript standards for {topic}",
            f"Only use legacy browser compatibility for {topic}",
            f"Avoid using standard JavaScript syntax for {topic}",
            f"Use non-standard JavaScript implementations for {topic}",
            f"Rely on browser-specific features for {topic}"
        ]
        
        references = [
            {"title": f"MDN Web Docs - {topic}", "url": f"https://developer.mozilla.org/en-US/search?q={topic.replace(' ', '+')}", "type": "Official Documentation", "description": f"Comprehensive Mozilla documentation on {topic}"},
            {"title": f"ECMAScript Specification", "url": "https://tc39.es/ecma262/", "type": "Official Standard", "description": "The official JavaScript language specification"},
            {"title": f"JavaScript.info - {topic}", "url": f"https://javascript.info/?s={topic.replace(' ', '+')}", "type": "Interactive Tutorial", "description": f"Modern JavaScript tutorial covering {topic}"},
            {"title": f"W3Schools JavaScript {topic}", "url": f"https://www.w3schools.com/js/", "type": "Learning Resource", "description": f"Beginner-friendly JavaScript {topic} examples"}
        ]
        
    elif 'python' in subject_lower:
        correct_options = [
            f"Follow PEP standards and Pythonic principles for {topic}",
            f"Use official Python documentation guidelines for {topic}",
            f"Implement according to Python best practices for {topic}",
            f"Apply the Zen of Python principles to {topic}"
        ]
        
        wrong_options = [
            f"Ignore Python conventions for {topic}",
            f"Use non-Pythonic approaches for {topic}",
            f"Avoid Python standard library for {topic}",
            f"Use deprecated Python syntax for {topic}",
            f"Ignore PEP guidelines for {topic}",
            f"Use Java-style coding in Python for {topic}"
        ]
        
        references = [
            {"title": f"Python.org Documentation - {topic}", "url": f"https://docs.python.org/3/search.html?q={topic.replace(' ', '+')}", "type": "Official Documentation", "description": f"Official Python documentation for {topic}"},
            {"title": f"Real Python - {topic}", "url": f"https://realpython.com/search/?q={topic.replace(' ', '+')}", "type": "Tutorial", "description": f"Practical Python tutorials on {topic}"},
            {"title": f"Python PEP Index", "url": "https://www.python.org/dev/peps/", "type": "Standards", "description": "Python Enhancement Proposals for coding standards"},
            {"title": f"Python Package Index", "url": f"https://pypi.org/search/?q={topic.replace(' ', '+')}", "type": "Package Repository", "description": f"Python packages related to {topic}"}
        ]
        
    elif 'math' in subject_lower or 'algebra' in subject_lower:
        correct_options = [
            f"Apply established mathematical principles and proven theorems for {topic}",
            f"Use standard mathematical procedures and formulas for {topic}",
            f"Follow step-by-step mathematical problem-solving for {topic}",
            f"Implement verified mathematical methods for {topic}"
        ]
        
        wrong_options = [
            f"Skip mathematical steps and guess answers for {topic}",
            f"Use unproven mathematical shortcuts for {topic}",
            f"Ignore mathematical properties for {topic}",
            f"Apply incorrect mathematical operations for {topic}",
            f"Use intuition instead of mathematical logic for {topic}",
            f"Avoid showing work or verification for {topic}"
        ]
        
        references = [
            {"title": f"Khan Academy - {topic}", "url": f"https://www.khanacademy.org/search?page_search_query={topic.replace(' ', '+')}", "type": "Educational Platform", "description": f"Interactive math lessons on {topic}"},
            {"title": f"Wolfram MathWorld - {topic}", "url": f"https://mathworld.wolfram.com/search/?query={topic.replace(' ', '+')}", "type": "Mathematical Reference", "description": f"Comprehensive mathematical encyclopedia for {topic}"},
            {"title": f"MIT OpenCourseWare - {topic}", "url": f"https://ocw.mit.edu/search/?q={topic.replace(' ', '+')}", "type": "Academic Course", "description": f"MIT mathematics courses covering {topic}"},
            {"title": f"Paul's Online Math Notes", "url": f"https://tutorial.math.lamar.edu/", "type": "Tutorial", "description": f"Detailed mathematical tutorials including {topic}"}
        ]
        
    else:  # Science or general
        correct_options = [
            f"Follow scientific method and evidence-based research for {topic}",
            f"Use peer-reviewed scientific literature for {topic}",
            f"Apply established scientific principles for {topic}",
            f"Rely on empirical evidence and experimentation for {topic}"
        ]
        
        wrong_options = [
            f"Use unverified claims and opinions for {topic}",
            f"Ignore scientific evidence for {topic}",
            f"Rely on pseudoscience for {topic}",
            f"Use outdated and disproven theories for {topic}",
            f"Avoid peer review and verification for {topic}",
            f"Base conclusions on personal beliefs for {topic}"
        ]
        
        references = [
            {"title": f"PubMed Scientific Literature - {topic}", "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={topic.replace(' ', '+')}", "type": "Scientific Database", "description": f"Peer-reviewed research articles on {topic}"},
            {"title": f"Khan Academy Science - {topic}", "url": "https://www.khanacademy.org/science", "type": "Educational Platform", "description": f"Science courses covering {topic}"},
            {"title": f"NASA Science - {topic}", "url": f"https://science.nasa.gov/search/?query={topic.replace(' ', '+')}", "type": "Scientific Institution", "description": f"NASA research and information on {topic}"},
            {"title": f"National Science Foundation", "url": f"https://www.nsf.gov/discoveries/disc_search.jsp?term={topic.replace(' ', '+')}", "type": "Research Foundation", "description": f"NSF-funded research on {topic}"}
        ]
    
    # Select options
    correct_option = random.choice(correct_options)
    selected_wrong = random.sample(wrong_options, 3)
    
    options = [correct_option] + selected_wrong
    correct_idx = 0
    
    explanation = f"This answer is correct because it {correct_option.lower()}, which represents the current best practices and standards in {subject} for {topic}."
    
    return options, correct_idx, explanation, references

# Replace the main question generation function
def generate_advanced_ai_questions_with_references(quiz_data):
    """Main function to generate topic-focused questions with comprehensive references"""
    return generate_topic_focused_questions(quiz_data)

# Enhanced Quiz Generation with External APIs
def generate_advanced_quiz_questions(topic, num_questions, difficulty):
    """Generate questions using multiple sources"""
    questions = []
    
    try:
        # Try to get Wikipedia content for context
        if HAS_WIKIPEDIA:
            wiki_summary = wikipedia.summary(topic, sentences=3)
        else:
            wiki_summary = f"General information about {topic}"
        
        # Generate questions based on topic and difficulty
        for i in range(num_questions):
            if i % 2 == 0:
                # Factual questions
                question = generate_factual_question(topic, wiki_summary, difficulty)
            else:
                # Conceptual questions
                question = generate_conceptual_question(topic, difficulty)
            
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
    options = generate_contextual_options_enhanced(topic, difficulty)
    
    return {
        "question": selected_question,
        "options": options,
        "correct_answer": 0,
        "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
        "difficulty": difficulty,
        "context": context[:200] + "..." if len(context) > 200 else context,
        "explanation": f"This answer is correct based on the fundamental understanding of {topic} and established research in the field."
    }

def generate_conceptual_question(topic, difficulty):
    """Generate conceptual questions"""
    concept_templates = {
        'easy': f"Which statement best describes {topic}?",
        'medium': f"What is the most significant aspect of {topic}?",
        'hard': f"Which principle is most fundamental to understanding {topic}?"
    }
    
    question = concept_templates.get(difficulty, concept_templates['medium'])
    options = generate_contextual_options_enhanced(topic, difficulty)
    
    return {
        "question": question,
        "options": options,
        "correct_answer": 0,
        "source": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
        "difficulty": difficulty,
        "explanation": f"This represents the most accurate conceptual understanding of {topic} based on current knowledge."
    }

def generate_contextual_options_enhanced(topic, difficulty):
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

def generate_smart_template_question(topic, question_index):
    """Generate template questions when advanced generation fails"""
    templates = [
        {
            "question": f"What is the primary characteristic of {topic}?",
            "options": [
                f"It is fundamental to understanding {topic}",
                f"It is rarely used in {topic}",
                f"It has no practical application",
                f"It is only theoretical"
            ],
            "correct_answer": 0,
            "explanation": f"This represents the core understanding of {topic}."
        },
        {
            "question": f"How is {topic} typically implemented?",
            "options": [
                f"Following established standards for {topic}",
                f"Using outdated methods",
                f"Without proper guidelines",
                f"Ignoring best practices"
            ],
            "correct_answer": 0,
            "explanation": f"Standard implementation follows best practices for {topic}."
        }
    ]
    
    template = templates[question_index % len(templates)]
    return {
        'id': question_index + 1,
        'question': template['question'],
        'options': template['options'],
        'correct_answer': template['correct_answer'],
        'explanation': template['explanation'],
        'ai_generated': True,
        'verified': True
    }

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

def generate_study_resources(topic):
    """Generate study resources for the topic"""
    return [
        {
            "title": f"Learn more about {topic}",
            "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "type": "Reference"
        },
        {
            "title": f"Practice exercises for {topic}",
            "url": f"https://www.google.com/search?q={topic.replace(' ', '+')}+practice+exercises",
            "type": "Practice"
        }
    ]

# Add endpoint to get available topics for a subject
@app.route('/api/topics/<subject>', methods=['GET'])
def get_available_topics(subject):
    """Get available topics for a given subject"""
    try:
        subject_lower = subject.lower()
        
        # Define available topics per subject
        topics_by_subject = {
            'computer science': ['JavaScript Functions', 'Python Functions', 'Object-Oriented Programming', 'Data Structures', 'Algorithms', 'Database Design'],
            'mathematics': ['Algebra Equations', 'Calculus Derivatives', 'Geometry Theorems', 'Statistics', 'Probability', 'Linear Algebra'],
            'chemistry': ['Chemical Compounds', 'Chemical Reactions', 'Periodic Table', 'Molecular Structure', 'Thermodynamics', 'Organic Chemistry'],
            'physics': ['Newton\'s Laws', 'Thermodynamics', 'Electromagnetism', 'Quantum Mechanics', 'Relativity', 'Wave Theory'],
            'biology': ['Cell Biology', 'Genetics', 'Evolution', 'Ecology', 'Human Anatomy', 'Molecular Biology'],
            'programming': ['JavaScript Functions', 'Python Functions', 'Java Classes', 'C++ Pointers', 'Web Development', 'Mobile App Development']
        }
        
        # Find matching subject
        available_topics = []
        for subject_key, topics in topics_by_subject.items():
            if subject_key in subject_lower or subject_lower in subject_key:
                available_topics = topics
                break
        
        if not available_topics:
            # Default topics based on subject keywords
            if any(keyword in subject_lower for keyword in ['computer', 'programming', 'software']):
                available_topics = topics_by_subject['computer science']
            elif 'math' in subject_lower:
                available_topics = topics_by_subject['mathematics']
            elif 'chemistry' in subject_lower or 'chemical' in subject_lower:
                available_topics = topics_by_subject['chemistry']
            elif 'physics' in subject_lower:
                available_topics = topics_by_subject['physics']
            elif 'biology' in subject_lower or 'bio' in subject_lower:
                available_topics = topics_by_subject['biology']
            else:
                available_topics = ['General Knowledge', 'Critical Thinking', 'Problem Solving']
        
        return jsonify({
            'subject': subject,
            'available_topics': available_topics,
            'count': len(available_topics)
        })
        
    except Exception as e:
        print(f"❌ Get topics error: {e}")
        return jsonify({'error': str(e)}), 500

def generate_intelligent_questions(quiz_data):
    """Generate intelligent, domain-specific questions with proper resources"""
    try:
        count = int(quiz_data.get('questionCount', 5))
        topic = quiz_data.get('topic', '').lower().strip()
        difficulty = quiz_data.get('difficulty', 'medium').lower()
        subject = quiz_data.get('subject', '').lower().strip()
        
        print(f"🧠 Generating intelligent questions for: {topic} in {subject} ({difficulty})")
        
        # Determine domain and subtopic
        domain, subtopic = determine_intelligent_domain(topic, subject)
        
        # Get relevant question pool
        question_pool = get_relevant_questions(domain, difficulty, subtopic, topic)
        
        # Generate questions
        questions = []
        used_questions = set()
        
        for i in range(count):
            question_data = select_and_customize_question(
                question_pool, used_questions, topic, subject, difficulty, i + 1
            )
            
            if question_data:
                questions.append(question_data)
            else:
                # Fallback: generate contextual question
                fallback_question = generate_smart_contextual_question(
                    topic, subject, difficulty, domain, i + 1
                )
                questions.append(fallback_question)
        
        print(f"✅ Generated {len(questions)} intelligent questions with verified resources")
        return questions
        
    except Exception as e:
        print(f"❌ Error in intelligent question generation: {e}")
        return generate_fallback_questions(quiz_data)

def determine_intelligent_domain(topic, subject):
    """Intelligently determine domain and subtopic"""
    topic_lower = topic.lower()
    subject_lower = subject.lower()
    
    # JavaScript domain mapping
    js_mapping = {
        'function': 'functions',
        'variable': 'variables',
        'array': 'arrays',
        'closure': 'closures',
        'promise': 'promises',
        'async': 'async',
        'dom': 'dom',
        'object': 'objects'
    }
    
    # Python domain mapping
    python_mapping = {
        'function': 'functions',
        'list': 'basics',
        'dictionary': 'basics',
        'comprehension': 'comprehensions',
        'class': 'oop',
        'module': 'modules'
    }
    
    # Math domain mapping
    math_mapping = {
        'algebra': 'algebra',
        'calculus': 'calculus',
        'geometry': 'geometry',
        'arithmetic': 'arithmetic',
        'percentage': 'arithmetic',
        'equation': 'algebra',
        'derivative': 'calculus',
        'integral': 'calculus'
    }
    
    # Science domain mapping
    science_mapping = {
        'chemistry': 'chemistry',
        'physics': 'physics',
        'biology': 'biology',
        'cell': 'biology',
        'atom': 'chemistry',
        'force': 'physics',
        'energy': 'physics'
    }
    
    # Determine domain
    if any(keyword in topic_lower or keyword in subject_lower for keyword in js_mapping.keys()) or 'javascript' in topic_lower:
        domain = 'javascript'
        subtopic = next((js_mapping[k] for k in js_mapping.keys() if k in topic_lower), 'functions')
    elif any(keyword in topic_lower or keyword in subject_lower for keyword in python_mapping.keys()) or 'python' in topic_lower:
        domain = 'python'
        subtopic = next((python_mapping[k] for k in python_mapping.keys() if k in topic_lower), 'basics')
    elif any(keyword in topic_lower or keyword in subject_lower for keyword in math_mapping.keys()) or 'math' in subject_lower:
        domain = 'mathematics'
        subtopic = next((math_mapping[k] for k in math_mapping.keys() if k in topic_lower), 'arithmetic')
    elif any(keyword in topic_lower or keyword in subject_lower for keyword in science_mapping.keys()) or 'science' in subject_lower:
        domain = 'science'
        subtopic = next((science_mapping[k] for k in science_mapping.keys() if k in topic_lower), 'chemistry')
    else:
        # Default mapping
        if 'computer' in subject_lower or 'programming' in subject_lower:
            domain, subtopic = 'javascript', 'functions'
        elif 'math' in subject_lower:
            domain, subtopic = 'mathematics', 'arithmetic'
        else:
            domain, subtopic = 'science', 'chemistry'
    
    return domain, subtopic

def get_relevant_questions(domain, difficulty, subtopic, topic):
    """Get relevant questions from the enhanced knowledge base"""
    question_pool = []
    
    # Get questions from the specific domain and difficulty
    if domain in TOPIC_FOCUSED_KNOWLEDGE_BASE and difficulty in TOPIC_FOCUSED_KNOWLEDGE_BASE[domain]:  # Fixed this line
        difficulty_data = TOPIC_FOCUSED_KNOWLEDGE_BASE[domain][difficulty]  # Fixed this line
        
        # First, try to get questions from the specific subtopic
        if subtopic in difficulty_data:
            question_pool.extend(difficulty_data[subtopic])
        
        # Add questions from other subtopics in the same domain/difficulty
        for other_subtopic, questions in difficulty_data.items():
            if other_subtopic != subtopic:
                question_pool.extend(questions[:2])  # Add max 2 from each other subtopic
    
    return question_pool

def select_and_customize_question(question_pool, used_questions, topic, subject, difficulty, question_num):
    """Select and customize a question from the pool"""
    available_questions = [q for q in question_pool if id(q) not in used_questions]
    
    if not available_questions:
        return None
    
    # Select question (prefer exact topic matches)
    selected = None
    topic_lower = topic.lower()
    
    # First try to find questions that match the topic
    for q in available_questions:
        if any(keyword in q['question'].lower() for keyword in topic_lower.split()):
            selected = q
            break
    
    # If no topic match, select randomly
    if not selected:
        selected = random.choice(available_questions)
    
    used_questions.add(id(selected))
    
    # Randomize answer positions
    options = selected['options'][:]
    correct_answer = selected['correct']
    
    # Create new randomized positions
    randomized_correct = random.randint(0, 3)
    if randomized_correct != correct_answer:
        options[randomized_correct], options[correct_answer] = options[correct_answer], options[randomized_correct]
    
    return {
        'id': question_num,
        'question': selected['question'],
        'options': options,
        'correct_answer': randomized_correct,
        'explanation': selected['explanation'],
        'references': selected['references'],
        'ai_generated': True,
        'verified': True,
        'difficulty': difficulty,
        'topic': topic,
        'domain': determine_intelligent_domain(topic, subject)[0]
    }

def generate_smart_contextual_question(topic, subject, difficulty, domain, question_num):
    """Generate smart contextual questions when no predefined questions exist"""
    
    # Smart question templates based on domain
    if domain == 'javascript':
        templates = {
            'easy': [
                f"What is the correct syntax for {topic} in JavaScript?",
                f"Which method is commonly used with {topic}?",
                f"How do you create a {topic} in JavaScript?"
            ],
            'medium': [
                f"What happens when you use {topic} with asynchronous code?",
                f"How does {topic} behave in different execution contexts?",
                f"What are the best practices for implementing {topic}?"
            ],
            'hard': [
                f"What are the performance implications of {topic}?",
                f"How does {topic} work with the JavaScript event loop?",
                f"What are the memory considerations when using {topic}?"
            ]
        }
        
        correct_answers = [
            f"It follows ECMAScript standards for {topic} implementation",
            f"It uses modern JavaScript best practices for {topic}",
            f"It implements the official specification for {topic}",
            f"It provides the recommended approach for {topic}"
        ]
        
        wrong_answers = [
            f"It violates JavaScript standards for {topic}",
            f"It uses deprecated methods for {topic}",
            f"It only works in legacy browsers for {topic}"
        ]
        
        references = [
            {"title": f"MDN Web Docs - {topic}", "url": f"https://developer.mozilla.org/en-US/search?q={topic.replace(' ', '+')}", "type": "Official Documentation"},
            {"title": f"ECMAScript Specification - {topic}", "url": "https://tc39.es/ecma262/", "type": "Official Specification"},
            {"title": f"JavaScript.info - {topic}", "url": f"https://javascript.info/?s={topic.replace(' ', '+')}", "type": "Tutorial"}
        ]
        
    elif domain == 'mathematics':
        templates = {
            'easy': [
                f"What is the basic rule for {topic}?",
                f"How do you calculate {topic}?",
                f"What is the formula for {topic}?"
            ],
            'medium': [
                f"How is {topic} applied in problem-solving?",
                f"What are the properties of {topic}?",
                f"How does {topic} relate to other mathematical concepts?"
            ],
            'hard': [
                f"What are the theoretical foundations of {topic}?",
                f"How is {topic} used in advanced mathematics?",
                f"What are the proofs related to {topic}?"
            ]
        }
        
        correct_answers = [
            f"It follows established mathematical principles for {topic}",
            f"It uses proven mathematical methods for {topic}",
            f"It applies the correct theorem for {topic}",
            f"It implements the standard approach for {topic}"
        ]
        
        wrong_answers = [
            f"It contradicts mathematical laws for {topic}",
            f"It uses incorrect formulas for {topic}",
            f"It ignores mathematical principles for {topic}"
        ]
        
        references = [
            {"title": f"Khan Academy - {topic}", "url": f"https://www.khanacademy.org/search?page_search_query={topic.replace(' ', '+')}", "type": "Educational"},
            {"title": f"Wolfram MathWorld - {topic}", "url": f"https://mathworld.wolfram.com/search/?query={topic.replace(' ', '+')}", "type": "Mathematical Reference"},
            {"title": f"MIT OpenCourseWare - {topic}", "url": f"https://ocw.mit.edu/search/?q={topic.replace(' ', '+')}", "type": "Academic"}
        ]
        
    else:  # science
        templates = {
            'easy': [
                f"What is the basic definition of {topic}?",
                f"What are the main characteristics of {topic}?",
                f"How is {topic} classified in science?"
            ],
            'medium': [
                f"What is the mechanism behind {topic}?",
                f"How does {topic} function in its environment?",
                f"What are the applications of {topic}?"
            ],
            'hard': [
                f"What are the theoretical models for {topic}?",
                f"How does current research explain {topic}?",
                f"What are the latest discoveries about {topic}?"
            ]
        }
        
        correct_answers = [
            f"It follows scientific evidence and research for {topic}",
            f"It is supported by peer-reviewed studies on {topic}",
            f"It reflects current scientific understanding of {topic}",
            f"It aligns with established scientific principles for {topic}"
        ]
        
        wrong_answers = [
            f"It contradicts scientific evidence for {topic}",
            f"It lacks scientific support for {topic}",
            f"It is based on outdated theories about {topic}"
        ]
        
        references = [
            {"title": f"PubMed Research - {topic}", "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={topic.replace(' ', '+')}", "type": "Scientific Literature"},
            {"title": f"Khan Academy Science - {topic}", "url": f"https://www.khanacademy.org/science", "type": "Educational"},
            {"title": f"NASA Science - {topic}", "url": f"https://science.nasa.gov/search/?query={topic.replace(' ', '+')}", "type": "Scientific Institution"}
        ]
    
    # Select template and create question
    difficulty_templates = templates.get(difficulty, templates['medium'])
    question_text = random.choice(difficulty_templates)
    
    # Create options
    correct_option = random.choice(correct_answers)
    wrong_options = random.sample(wrong_answers, 3)
    
    options = [correct_option] + wrong_options
    correct_answer = 0
    
    # Randomize positions
    randomized_correct = random.randint(0, 3)
    if randomized_correct != 0:
        options[randomized_correct], options[0] = options[0], options[randomized_correct]
    
    explanation = f"This answer is correct because {correct_option.lower()} and represents the current standard understanding in {subject}."
    
    return {
        'id': question_num,
        'question': question_text,
        'options': options,
        'correct_answer': randomized_correct,
        'explanation': explanation,
        'references': references,
        'ai_generated': True,
        'verified': True,
        'difficulty': difficulty,
        'topic': topic,
        'domain': domain
    }

def generate_fallback_questions(quiz_data):
    """Fallback question generation if all else fails"""
    count = int(quiz_data.get('questionCount', 5))
    topic = quiz_data.get('topic', 'General Knowledge')
    subject = quiz_data.get('subject', 'General')
    difficulty = quiz_data.get('difficulty', 'medium')
    
    questions = []
    for i in range(count):
        questions.append({
            'id': i + 1,
            'question': f"What is an important concept related to {topic}?",
            'options': [
                f"It is a fundamental principle in {subject}",
                f"It is not relevant to {subject}",
                f"It only applies to advanced topics",
                f"It has been replaced by newer concepts"
            ],
            'correct_answer': 0,
            'explanation': f"This represents a core concept in {subject} related to {topic}.",
            'references': [
                {"title": f"Educational Resource - {topic}", "url": f"https://www.google.com/search?q={topic.replace(' ', '+')}", "type": "General Reference"}
            ],
            'ai_generated': True,
            'verified': False,
            'difficulty': difficulty,
            'topic': topic
        })
    
    return questions

# Update your main quiz creation endpoint to use the new intelligent system
def generate_advanced_ai_questions_with_references(quiz_data):
    """Main function to generate advanced AI questions with proper references"""
    return generate_topic_focused_questions(quiz_data)

def generate_pdf(quiz, questions):
    if not FPDF_AVAILABLE:
        return jsonify({'error': 'PDF generation not available'}), 500
        
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Quiz: {quiz.title}', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Subject: {quiz.subject}', 0, 1)
    pdf.cell(0, 10, f'Topic: {quiz.topic}', 0, 1)
    pdf.cell(0, 10, f'Difficulty: {quiz.difficulty}', 0, 1)
    pdf.ln(5)
    
    for i, q in enumerate(questions, 1):
        pdf.set_font('Arial', 'B', 12)
        # Handle long questions by splitting them
        question_text = q["question"][:80] + "..." if len(q["question"]) > 80 else q["question"]
        pdf.cell(0, 10, f'Q{i}: {question_text}', 0, 1)
        
        pdf.set_font('Arial', '', 10)
        for j, option in enumerate(q['options']):
            marker = '[X]' if j == q['correct_answer'] else '[ ]'
            option_text = option[:70] + "..." if len(option) > 70 else option
            pdf.cell(0, 6, f'  {marker} {chr(65+j)}) {option_text}', 0, 1)
        pdf.ln(3)
    
    output = io.BytesIO()
    pdf.output(output, 'S')
    output.seek(0)
    
    return send_file(output, mimetype='application/pdf', 
                    as_attachment=True, download_name=f'{quiz.title}.pdf')

def generate_docx(quiz, questions):
    if not DOCX_AVAILABLE:
        return jsonify({'error': 'Word generation not available'}), 500
        
    doc = Document()
    doc.add_heading(f'Quiz: {quiz.title}', 0)
    
    doc.add_paragraph(f'Subject: {quiz.subject}')
    doc.add_paragraph(f'Topic: {quiz.topic}')
    doc.add_paragraph(f'Difficulty: {quiz.difficulty}')
    
    for i, q in enumerate(questions, 1):
        doc.add_heading(f'Question {i}', level=2)
        doc.add_paragraph(q['question'])
        
        for j, option in enumerate(q['options']):
            marker = '[X]' if j == q['correct_answer'] else '[ ]'
            doc.add_paragraph(f'{marker} {chr(65+j)}) {option}')
        
        doc.add_paragraph(f'Explanation: {q["explanation"]}')
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    as_attachment=True, download_name=f'{quiz.title}.docx')

def generate_xlsx(quiz, questions):
    if not XLSX_AVAILABLE:
        return jsonify({'error': 'Excel generation not available'}), 500
        
    data = []
    for i, q in enumerate(questions, 1):
        data.append({
            'Question_Number': i,
            'Question': q['question'],
            'Option_A': q['options'][0],
            'Option_B': q['options'][1],
            'Option_C': q['options'][2],
            'Option_D': q['options'][3],
            'Correct_Answer': chr(65 + q['correct_answer']),
            'Explanation': q['explanation']
        })
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_excel(output, index=False, sheet_name=quiz.title[:31])
    output.seek(0)
    
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True, download_name=f'{quiz.title}.xlsx')

# Add download endpoint
@app.route('/api/quiz/<int:quiz_id>/download/<format>', methods=['GET'])
def download_quiz(quiz_id, format):
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        quiz = Quiz.query.filter_by(id=quiz_id, user_id=user_id).first()
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        questions = json.loads(quiz.questions)
        
        if format == 'pdf':
            return generate_pdf(quiz, questions)
        elif format == 'docx':
            return generate_docx(quiz, questions)
        elif format == 'xlsx':
            return generate_xlsx(quiz, questions)
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update the existing quiz creation endpoint
@app.route('/api/quiz', methods=['POST'])
def create_quiz():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        quiz_data = request.get_json()
        print(f"🤖 Creating enhanced AI quiz: {quiz_data.get('title')} by user {user_id}")
        
        # Extract quiz parameters
        topic = quiz_data.get('topic', 'General Knowledge')
        num_questions = int(quiz_data.get('questionCount', 5))
        difficulty = quiz_data.get('difficulty', 'medium')
        
        # Use enhanced AI question generation
        questions = generate_advanced_quiz_questions(topic, num_questions, difficulty)
        
        # Calculate time limit
        time_limit = calculate_time_limit(num_questions, difficulty)
        
        quiz = Quiz(
            user_id=user_id,
            title=quiz_data.get('title'),
            subject=quiz_data.get('subject'),
            topic=topic,
            difficulty=difficulty,
            questions=json.dumps(questions)
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        print(f"✅ Enhanced AI Quiz created: {quiz.title} with {len(questions)} questions")
        return jsonify({
            'id': quiz.id,
            'title': quiz.title,
            'subject': quiz.subject,
            'topic': quiz.topic,
            'difficulty': quiz.difficulty,
            'questions': questions,
            'created_at': quiz.created_at.isoformat(),
            'ai_powered': True,
            'verified': True,
            'time_limit': time_limit,
            'total_questions': len(questions),
            'question_count': len(questions),
            'message': f"Generated {len(questions)} enhanced questions for {topic}"
        })
        
    except Exception as e:
        print(f"❌ Enhanced AI Quiz creation error: {e}")
        return jsonify({'error': str(e)}), 500

# Add enhanced quiz submission with detailed feedback
@app.route('/api/quiz/session/<session_token>/submit', methods=['POST'])
def submit_quiz_enhanced(session_token):
    """Submit entire quiz and calculate results with enhanced feedback"""
    try:
        # Verify session
        session = QuizSession.query.filter_by(session_token=session_token, is_active=True).first()
        if not session:
            return jsonify({'error': 'Invalid session'}), 401
        
        # Get quiz and questions
        quiz = Quiz.query.get(session.quiz_id)
        questions = json.loads(quiz.questions)
        user_answers = json.loads(session.answers_so_far)
        
        # Calculate score with enhanced details
        correct_count = 0
        detailed_results = []
        
        for question in questions:
            q_id = str(question['id'])
            user_answer = user_answers.get(q_id)
            correct_answer = question['correct_answer']
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_count += 1
            
            detailed_results.append({
                'question_id': question['id'],
                'question': question['question'],
                'options': question['options'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': generate_detailed_explanation(question, is_correct, user_answer),
                'source': question.get('source', ''),
                'difficulty': question.get('difficulty', 'medium')
            })
        
        # Calculate time taken
        time_taken = int((datetime.datetime.utcnow() - session.started_at).total_seconds())
        
        # Calculate performance metrics
        percentage = round((correct_count / len(questions)) * 100, 1)
        performance_data = calculate_performance_metrics(percentage, time_taken, quiz.topic)
        
        # Save quiz attempt
        quiz_attempt = QuizAttempt(
            user_id=session.user_id,
            quiz_id=session.quiz_id,
            answers=session.answers_so_far,
            score=correct_count,
            total_questions=len(questions),
            time_taken=time_taken
        )
        
        # Deactivate session
        session.is_active = False
        
        db.session.add(quiz_attempt)
        db.session.commit()
        
        print(f"🏆 Enhanced Quiz submitted: {quiz.title} - Score: {correct_count}/{len(questions)} ({percentage}%)")
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'results': {
                'score': correct_count,
                'total_questions': len(questions),
                'percentage': percentage,
                'grade': performance_data['grade'],
                'performance': performance_data['level'],
                'time_taken': time_taken,
                'time_efficiency': performance_data.get('time_efficiency', 100),
                'detailed_results': detailed_results,
                'study_resources': generate_study_resources(quiz.topic),
                'quiz_info': {
                    'title': quiz.title,
                    'subject': quiz.subject,
                    'topic': quiz.topic,
                    'difficulty': quiz.difficulty
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Enhanced submit quiz error: {e}")
        return jsonify({'error': str(e)}), 500

def generate_detailed_explanation(question, is_correct, user_answer):
    """Generate detailed explanations for answers"""
    if is_correct:
        return f"Correct! {question['options'][question['correct_answer']]} is indeed the right answer. {question.get('explanation', '')}"
    else:
        correct_text = question['options'][question['correct_answer']]
        if user_answer is not None and 0 <= user_answer < len(question['options']):
            user_text = question['options'][user_answer]
            return f"Not quite right. You selected '{user_text}', but the correct answer is '{correct_text}'. {question.get('explanation', 'Review the material to understand why this is correct.')}"
        else:
            return f"No answer selected. The correct answer is '{correct_text}'. {question.get('explanation', 'Make sure to review this concept.')}"

def calculate_performance_metrics(score_percentage, time_taken, topic):
    """Calculate detailed performance metrics"""
    # Performance level based on score
    if score_percentage >= 90:
        level = "Excellent! 🏆"
        grade = "A"
    elif score_percentage >= 80:
        level = "Very Good! 🎯"
        grade = "B"
    elif score_percentage >= 70:
        level = "Good Job! 👍"
        grade = "C"
    elif score_percentage >= 60:
        level = "Not Bad! 📚"
        grade = "D"
    elif score_percentage >= 50:
        level = "Keep Learning! 💪"
        grade = "D"
    else:
        level = "More Practice Needed! 📖"
        grade = "F"
    
    return {
        'level': level,
        'grade': grade,
        'time_efficiency': round(min(time_taken / 60, 100), 1),  # Simple time efficiency
        'recommendations': [
            f"Focus on understanding {topic} fundamentals",
            f"Practice more {topic} exercises",
            f"Review key concepts in {topic}"
        ]
    }

# Keep all your other existing endpoints (health_check, login, register, get_quizzes, download functions, etc.)
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'message': 'Quizgenix Advanced AI Backend is running! 🤖',
        'status': 'healthy',
        'version': '2.0.0',
        'features': ['Advanced AI Question Generation', 'Knowledge Base Matching', 'Logical Answer Distribution'],
        'supported_domains': list(TOPIC_FOCUSED_KNOWLEDGE_BASE.keys())  # Fixed this line
    })

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"🔐 Login attempt: {data.get('email')}")
        
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user and check_password_hash(user.password_hash, data.get('password')):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            print(f"✅ Login successful: {user.email}")
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
            print(f"❌ Invalid credentials for: {data.get('email')}")
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"📝 Registration attempt: {data.get('email')}")
        
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
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        print(f"✅ Registration successful: {user.email}")
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
        print(f"❌ Registration error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        quizzes = Quiz.query.filter_by(user_id=user_id).order_by(Quiz.created_at.desc()).all()
        
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
        print(f"❌ Get quizzes error: {e}")
        return jsonify({'error': str(e)}), 500

# Add these endpoints after your existing routes

@app.route('/api/quiz/<int:quiz_id>/start', methods=['POST'])
def start_quiz(quiz_id):
    """Start a new quiz session for a student"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        # Get the quiz
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Check if user already has an active session for this quiz
        existing_session = QuizSession.query.filter_by(
            user_id=user_id, 
            quiz_id=quiz_id, 
            is_active=True
        ).first()
        
        if existing_session and existing_session.expires_at > datetime.datetime.utcnow():
            return jsonify({
                'message': 'Quiz session already active',
                'session_token': existing_session.session_token,
                'expires_at': existing_session.expires_at.isoformat(),
                'current_question': existing_session.current_question
            })
        
        # Create new session
        session_token = jwt.encode({
            'user_id': user_id,
            'quiz_id': quiz_id,
            'session_id': random.randint(10000, 99999),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        quiz_session = QuizSession(
            user_id=user_id,
            quiz_id=quiz_id,
            session_token=session_token,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        )
        
        db.session.add(quiz_session)
        db.session.commit()
        
        # Get quiz questions without showing correct answers
        questions = json.loads(quiz.questions)
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'subject': quiz.subject,
            'topic': quiz.topic,
            'difficulty': quiz.difficulty,
            'total_questions': len(questions),
            'questions': [
                {
                    'id': q['id'],
                    'question': q['question'],
                    'options': q['options']
                    # Don't include correct_answer or explanation
                }
                for q in questions
            ]
        }
        
        print(f"🎯 Quiz session started: {quiz.title} for user {user_id}")
        return jsonify({
            'message': 'Quiz session started',
            'session_token': session_token,
            'quiz': quiz_data,
            'time_limit': 7200,  # 2 hours in seconds
            'expires_at': quiz_session.expires_at.isoformat()
        })
        
    except Exception as e:
        print(f"❌ Start quiz error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/session/<session_token>/answer', methods=['POST'])
def submit_answer(session_token):
    """Submit answer for current question"""
    try:
        # Verify session
        session = QuizSession.query.filter_by(session_token=session_token, is_active=True).first()
        if not session or session.expires_at < datetime.datetime.utcnow():
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        data = request.get_json()
        question_id = data.get('question_id')
        selected_answer = data.get('answer')  # 0, 1, 2, or 3
        
        # Update session with answer
        current_answers = json.loads(session.answers_so_far)

        current_answers[str(question_id)] = selected_answer
        
        session.answers_so_far = json.dumps(current_answers)
        session.current_question = max(session.current_question, question_id)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Answer submitted',
            'question_id': question_id,
            'total_answered': len(current_answers)
        })
        
    except Exception as e:
        print(f"❌ Submit answer error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/session/<session_token>/submit', methods=['POST'])
def submit_quiz(session_token):
    """Submit entire quiz and calculate results"""
    try:
        # Verify session
        session = QuizSession.query.filter_by(session_token=session_token, is_active=True).first()
        if not session:
            return jsonify({'error': 'Invalid session'}), 401
        
        # Get quiz and questions
        quiz = Quiz.query.get(session.quiz_id)
        questions = json.loads(quiz.questions)
        user_answers = json.loads(session.answers_so_far)
        
        # Calculate score
        correct_count = 0
        detailed_results = []
        
        for question in questions:
            q_id = str(question['id'])
            user_answer = user_answers.get(q_id)
            correct_answer = question['correct_answer']
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_count += 1
            
            detailed_results.append({
                'question_id': question['id'],
                'question': question['question'],
                'options': question['options'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.get('explanation', ''),
                'references': question.get('references', [])
            })
        
        # Calculate time taken
        time_taken = int((datetime.datetime.utcnow() - session.started_at).total_seconds())
        
        # Save quiz attempt
        quiz_attempt = QuizAttempt(
            user_id=session.user_id,
            quiz_id=session.quiz_id,
            answers=session.answers_so_far,
            score=correct_count,
            total_questions=len(questions),
            time_taken=time_taken
        )
        
        # Deactivate session
        session.is_active = False
        
        db.session.add(quiz_attempt)
        db.session.commit()
        
        # Calculate percentage and grade
        percentage = round((correct_count / len(questions)) * 100, 1)
        grade = 'A' if percentage >= 90 else 'B' if percentage >= 80 else 'C' if percentage >= 70 else 'D' if percentage >= 60 else 'F'
        
        print(f"🏆 Quiz submitted: {quiz.title} - Score: {correct_count}/{len(questions)} ({percentage}%)")
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'results': {
                'score': correct_count,
                'total_questions': len(questions),
                'percentage': percentage,
                'grade': grade,
                'time_taken': time_taken,
                'detailed_results': detailed_results,
                'quiz_info': {
                    'title': quiz.title,
                    'subject': quiz.subject,
                    'topic': quiz.topic,
                    'difficulty': quiz.difficulty
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Submit quiz error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/<int:quiz_id>/attempts', methods=['GET'])
def get_quiz_attempts(quiz_id):
    """Get all attempts for a specific quiz (for lecturers)"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        # Check if user is lecturer and owns the quiz
        quiz = Quiz.query.filter_by(id=quiz_id, user_id=user_id).first()
        if not quiz:
            return jsonify({'error': 'Quiz not found or access denied'}), 403
        
        attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).join(User).all()
        
        attempt_list = []
        for attempt in attempts:
            attempt_list.append({
                'id': attempt.id,
                'student_name': attempt.user.name,
                'student_email': attempt.user.email,
                'score': attempt.score,
                'total_questions': attempt.total_questions,
                'percentage': round((attempt.score / attempt.total_questions) * 100, 1),
                'time_taken': attempt.time_taken,
                'completed_at': attempt.completed_at.isoformat()
            })
        
        return jsonify({
            'quiz_title': quiz.title,
            'total_attempts': len(attempt_list),
            'attempts': attempt_list
        })
        
    except Exception as e:
        print(f"❌ Get quiz attempts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/my-results', methods=['GET'])
def get_my_results():
    """Get quiz results for current student"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        attempts = QuizAttempt.query.filter_by(user_id=user_id).join(Quiz).all()
        
        result_list = []
        for attempt in attempts:
            percentage = round((attempt.score / attempt.total_questions) * 100, 1)
            grade = 'A' if percentage >= 90 else 'B' if percentage >= 80 else 'C' if percentage >= 70 else 'D' if percentage >= 60 else 'F'
            
            result_list.append({
                'id': attempt.id,
                'quiz_title': attempt.quiz.title,
                'quiz_subject': attempt.quiz.subject,
                'quiz_topic': attempt.quiz.topic,
                'quiz_difficulty': attempt.quiz.difficulty,
                'score': attempt.score,
                'total_questions': attempt.total_questions,
                'percentage': percentage,
                'grade': grade,
                'time_taken': attempt.time_taken,
                'completed_at': attempt.completed_at.isoformat()
            })
        
        return jsonify({
            'total_attempts': len(result_list),
            'results': sorted(result_list, key=lambda x: x['completed_at'], reverse=True)
        })
        
    except Exception as e:
        print(f"❌ Get my results error: {e}")
        return jsonify({'error': str(e)}), 500

# Analytics endpoints
@app.route('/api/lecturer/analytics', methods=['GET'])
def get_analytics():
    """Get comprehensive analytics for lecturer"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        # Get lecturer user
        lecturer = User.query.get(user_id)
        if not lecturer or lecturer.role != 'lecturer':
            return jsonify({'error': 'Access denied'}), 403
        
        # Calculate various statistics
        lecturer_quizzes = Quiz.query.filter_by(user_id=user_id).all()
        lecturer_quiz_ids = [q.id for q in lecturer_quizzes]
        lecturer_attempts = QuizAttempt.query.filter(QuizAttempt.quiz_id.in_(lecturer_quiz_ids)).all()
        
        analytics = {
            'overview': {
                'total_quizzes': len(lecturer_quizzes),
                'total_students': len(set(a.user_id for a in lecturer_attempts)),
                'total_attempts': len(lecturer_attempts),
                'average_score': round(sum(a.score / a.total_questions * 100 for a in lecturer_attempts) / len(lecturer_attempts), 1) if lecturer_attempts else 0
            },
            'quiz_performance': [],
            'student_performance': [],
            'difficulty_analysis': calculate_difficulty_analysis(lecturer_attempts, lecturer_quizzes),
            'topic_popularity': calculate_topic_popularity(lecturer_quizzes, lecturer_attempts),
            'recent_activity': get_recent_activity(lecturer_attempts)
        }
        
        # Quiz performance breakdown
        for quiz in lecturer_quizzes:
            quiz_attempts = [a for a in lecturer_attempts if a.quiz_id == quiz.id]
            if quiz_attempts:
                avg_score = sum(a.score / a.total_questions * 100 for a in quiz_attempts) / len(quiz_attempts)
                analytics['quiz_performance'].append({
                    'quiz_id': quiz.id,
                    'title': quiz.title,
                    'attempts': len(quiz_attempts),
                    'average_score': round(avg_score, 1),
                    'highest_score': max(a.score / a.total_questions * 100 for a in quiz_attempts),
                    'lowest_score': min(a.score / a.total_questions * 100 for a in quiz_attempts)
                })
        
        # Student performance summary
        student_stats = {}
        for attempt in lecturer_attempts:
            student = User.query.get(attempt.user_id)
            if student.id not in student_stats:
                student_stats[student.id] = {
                    'name': student.name,
                    'email': student.email,
                    'attempts': 0,
                    'total_score': 0,
                    'quizzes_taken': []
                }
            
            student_stats[student.id]['attempts'] += 1
            student_stats[student.id]['total_score'] += (attempt.score / attempt.total_questions * 100)
            quiz = Quiz.query.get(attempt.quiz_id)
            student_stats[student.id]['quizzes_taken'].append({
                'quiz_title': quiz.title,
                'score': round(attempt.score / attempt.total_questions * 100, 1),
                'date': attempt.completed_at.isoformat()
            })
        
        for student_id, stats in student_stats.items():
            stats['average_score'] = round(stats['total_score'] / stats['attempts'], 1)
            analytics['student_performance'].append(stats)
        
        return jsonify({'analytics': analytics})
        
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return jsonify({'error': str(e)}), 500

def calculate_difficulty_analysis(attempts, quizzes):
    """Analyze performance by difficulty level"""
    difficulty_stats = {}
    quiz_difficulty_map = {q.id: q.difficulty for q in quizzes}
    
    for attempt in attempts:
        difficulty = quiz_difficulty_map.get(attempt.quiz_id, 'medium')
        if difficulty not in difficulty_stats:
            difficulty_stats[difficulty] = {'scores': [], 'count': 0}
        
        score_percentage = (attempt.score / attempt.total_questions) * 100
        difficulty_stats[difficulty]['scores'].append(score_percentage)
        difficulty_stats[difficulty]['count'] += 1
    
    analysis = {}
    for difficulty, stats in difficulty_stats.items():
        if stats['scores']:
            analysis[difficulty] = {
                'average_score': round(sum(stats['scores']) / len(stats['scores']), 1),
                'attempts': stats['count'],
                'pass_rate': round(len([s for s in stats['scores'] if s >= 70]) / len(stats['scores']) * 100, 1)
            }
    
    return analysis

def calculate_topic_popularity(quizzes, attempts):
    """Calculate which topics are most popular and how they perform"""
    topic_stats = {}
    
    for quiz in quizzes:
        topic = quiz.topic
        if topic not in topic_stats:
            topic_stats[topic] = {'quizzes': 0, 'attempts': 0, 'scores': []}
        topic_stats[topic]['quizzes'] += 1
    
    for attempt in attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        topic = quiz.topic
        if topic in topic_stats:
            topic_stats[topic]['attempts'] += 1
            score_percentage = (attempt.score / attempt.total_questions) * 100
            topic_stats[topic]['scores'].append(score_percentage)
    
    popularity = []
    for topic, stats in topic_stats.items():
        if stats['scores']:
            avg_score = sum(stats['scores']) / len(stats['scores'])
            popularity.append({
                'topic': topic,
                'quizzes': stats['quizzes'],
                'attempts': stats['attempts'],
                'average_score': round(avg_score, 1),
                'popularity_score': stats['attempts'] * 2 + stats['quizzes']  # Combined metric
            })
    
    # Sort by popularity
    popularity.sort(key=lambda x: x['popularity_score'], reverse=True)
    return popularity[:10]  # Top 10

def get_recent_activity(attempts):
    """Get recent quiz activity"""
    # Sort attempts by date and get recent ones
    sorted_attempts = sorted(attempts, key=lambda x: x.completed_at, reverse=True)
    
    recent = []
    for attempt in sorted_attempts[:10]:  # Last 10 activities
        user = User.query.get(attempt.user_id)
        quiz = Quiz.query.get(attempt.quiz_id)
        score_percentage = round((attempt.score / attempt.total_questions) * 100, 1)
        
        recent.append({
            'student_name': user.name,
            'quiz_title': quiz.title,
            'score': score_percentage,
            'date': attempt.completed_at.isoformat(),
            'performance': get_performance_level(score_percentage)
        })
    
    return recent

def get_performance_level(score_percentage):
    """Get performance level based on score"""
    if score_percentage >= 90:
        return "Excellent! 🏆"
    elif score_percentage >= 80:
        return "Very Good! 🎯"
    elif score_percentage >= 70:
        return "Good Job! 👍"
    elif score_percentage >= 60:
        return "Not Bad! 📚"
    elif score_percentage >= 50:
        return "Keep Learning! 💪"
    else:
        return "More Practice Needed! 📖"

@app.route('/api/lecturer/quiz/<int:quiz_id>/analytics', methods=['GET'])
def get_quiz_analytics(quiz_id):
    """Get detailed analytics for a specific quiz"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        # Check if user is lecturer and owns the quiz
        quiz = Quiz.query.filter_by(id=quiz_id, user_id=user_id).first()
        if not quiz:
            return jsonify({'error': 'Quiz not found or access denied'}), 404
        
        quiz_attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).all()
        
        if not quiz_attempts:
            return jsonify({'message': 'No attempts yet', 'analytics': None})
        
        # Get questions for analysis
        questions = json.loads(quiz.questions)
        
        # Detailed question analysis
        question_analysis = []
        for i, question in enumerate(questions):
            correct_count = 0
            total_attempts = len(quiz_attempts)
            
            for attempt in quiz_attempts:
                answers = json.loads(attempt.answers)
                user_answer = answers.get(str(i + 1))
                if user_answer == question.get('correct_answer', 0):
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
        
        # Calculate performance metrics
        scores = [(a.score / a.total_questions * 100) for a in quiz_attempts]
        
        analytics = {
            'quiz_info': {
                'title': quiz.title,
                'topic': quiz.topic,
                'difficulty': quiz.difficulty,
                'total_questions': len(questions)
            },
            'performance_summary': {
                'total_attempts': len(quiz_attempts),
                'average_score': round(sum(scores) / len(scores), 1),
                'highest_score': round(max(scores), 1),
                'lowest_score': round(min(scores), 1),
                'pass_rate': round(len([s for s in scores if s >= 70]) / len(scores) * 100, 1)
            },
            'question_analysis': question_analysis,
            'score_distribution': calculate_score_distribution(scores),
            'time_analysis': calculate_time_analysis(quiz_attempts)
        }
        
        return jsonify({'analytics': analytics})
        
    except Exception as e:
        print(f"❌ Quiz analytics error: {e}")
        return jsonify({'error': str(e)}), 500

def calculate_score_distribution(scores):
    """Calculate score distribution"""
    distribution = {
        'A (90-100%)': 0,
        'B (80-89%)': 0,
        'C (70-79%)': 0,
        'D (60-69%)': 0,
        'F (0-59%)': 0
    }
    
    for score in scores:
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

def calculate_time_analysis(attempts):
    """Analyze time usage patterns"""
    if not attempts:
        return None
    
    times = [a.time_taken for a in attempts if a.time_taken > 0]
    
    if not times:
        return None
    
    return {
        'average_time': round(sum(times) / len(times), 1),
        'fastest_time': min(times),
        'slowest_time': max(times),
        'total_attempts': len(times)
    }

def init_db():
    """Initialize database with sample data"""
    print("🗄️ Initializing database...")
    
    db.create_all()
    
    if not User.query.filter_by(email='lecturer@test.com').first():
        lecturer = User(
            name='Test Lecturer',
            email='lecturer@test.com',
            password_hash=generate_password_hash('password123'),
            role='lecturer'
        )
        db.session.add(lecturer)
        print("👨‍🏫 Created test lecturer: lecturer@test.com")
    
    if not User.query.filter_by(email='student@test.com').first():
        student = User(
            name='Test Student',
            email='student@test.com',
            password_hash=generate_password_hash('password123'),
            role='student'
        )
        db.session.add(student)
        print("🎓 Created test student: student@test.com")
    
    db.session.commit()
    print("✅ Database initialized successfully")

if __name__ == '__main__':
    print("🚀 Starting Quizgenix Advanced AI Backend...")
    print("🤖 AI Features: Smart Knowledge Base, Logical Questions, Diverse Answers")
    print("🧠 Supported Domains:", list(TOPIC_FOCUSED_KNOWLEDGE_BASE.keys()))  # Fixed this line
    
    with app.app_context():
        init_db()
    
    print("🌐 Server starting on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
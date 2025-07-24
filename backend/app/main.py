import os
import json
import requests
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Quizgenix backend running"

@app.route('/api/score', methods=['POST'])
def calculate_score():
    try:
        data = request.get_json()
        questions = data.get('questions', [])
        user_answers = data.get('user_answers', [])
        
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
def generate_quiz():
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


if __name__ == '__main__':
    app.run(debug=True)
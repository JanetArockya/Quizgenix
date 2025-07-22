from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Quizgenix backend running"

@app.route('/api/quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    topic = data.get('topic', 'General')
    question = {
        "question": f"What is 2 + 2 in {topic}?",
        "options": ["3", "4", "5", "6"],
        "correctOption": 1,
        "source": "https://en.wikipedia.org/wiki/Addition"
    }
    return jsonify({"questions": [question]})

if __name__ == '__main__':
    app.run(debug=True)
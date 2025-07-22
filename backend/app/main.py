import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def home():
    return "Quizgenix backend running"

@app.route('/api/quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.get_json()
        topic = data.get('topic', 'General Knowledge')

        prompt = f"""
        Generate a single multiple-choice question about the topic: {topic}.
        The question should be challenging but fair.
        Provide four options, with one correct answer.
        Also, provide a credible source URL for the answer.

        Return the response as a valid JSON object with the following structure:
        {{
            "question": "Your question here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correctOption": index_of_correct_option,
            "source": "URL to a credible source"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to generate quiz questions in JSON format."},
                {"role": "user", "content": prompt}
            ]
        )

        # The response from the API is a stringified JSON, so we need to parse it.
        question_data = json.loads(response.choices[0].message.content)

        # The API might return the question data wrapped in a list or another object
        # We need to ensure we return a consistent format for the frontend
        if isinstance(question_data, list):
             final_question = question_data[0]
        else:
             final_question = question_data

        return jsonify({"questions": [final_question]})

    except Exception as e:
        print(f"An error occurred: {e}")
        # In case of an error (e.g., API key issue, parsing error), return a fallback question
        fallback_question = {
            "question": "The AI is currently offline. What is the capital of France?",
            "options": ["Berlin", "Madrid", "Paris", "Rome"],
            "correctOption": 2,
            "source": "https://en.wikipedia.org/wiki/Paris"
        }
        return jsonify({"questions": [fallback_question]}), 500


if __name__ == '__main__':
    app.run(debug=True)
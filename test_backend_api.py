#!/usr/bin/env python3
"""
Backend API Tester for Quizgenix
This script tests all the backend endpoints to verify data is being saved correctly
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_api_endpoints():
    """Test all backend API endpoints"""
    print("🚀 Testing Quizgenix Backend API Endpoints")
    print("="*50)
    
    # Test health/status
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Base endpoint: {response.status_code}")
    except:
        print("❌ Backend server not running or unreachable")
        return
    
    # Test user registration
    print("\n📝 Testing User Registration...")
    user_data = {
        "name": "Test API User",
        "email": f"api-test-{datetime.now().strftime('%H%M%S')}@test.com",
        "password": "testpass123",
        "role": "student"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=user_data)
        if response.status_code == 201:
            print("✅ User registration successful")
            user_result = response.json()
            print(f"   User ID: {user_result.get('user_id')}")
        else:
            print(f"⚠️ User registration: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ User registration error: {e}")
    
    # Test user login
    print("\n🔐 Testing User Login...")
    login_data = {
        "email": "student@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login successful")
            login_result = response.json()
            token = login_result.get('token')
            print(f"   Token received: {token[:20]}...")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"⚠️ User login: {response.status_code} - {response.text}")
            headers = {}
    except Exception as e:
        print(f"❌ User login error: {e}")
        headers = {}
    
    # Test get quizzes
    print("\n📋 Testing Get Quizzes...")
    try:
        response = requests.get(f"{BASE_URL}/api/quizzes", headers=headers)
        if response.status_code == 200:
            quizzes = response.json()
            print(f"✅ Retrieved {len(quizzes)} quizzes")
            if quizzes:
                print(f"   First quiz: {quizzes[0].get('title', 'N/A')}")
        else:
            print(f"⚠️ Get quizzes: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Get quizzes error: {e}")
    
    # Test quiz generation
    print("\n🎯 Testing Quiz Generation...")
    quiz_data = {
        "title": "API Test Quiz",
        "subject": "Computer Science",
        "topic": "Testing",
        "difficulty": "easy",
        "num_questions": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/quiz", json=quiz_data, headers=headers)
        if response.status_code == 201:
            print("✅ Quiz generation successful")
            quiz_result = response.json()
            print(f"   Quiz ID: {quiz_result.get('quiz_id')}")
            print(f"   Questions generated: {len(quiz_result.get('questions', []))}")
            generated_quiz_id = quiz_result.get('quiz_id')
        else:
            print(f"⚠️ Quiz generation: {response.status_code} - {response.text}")
            generated_quiz_id = None
    except Exception as e:
        print(f"❌ Quiz generation error: {e}")
        generated_quiz_id = None
    
    # Test quiz start and submission (if we have a quiz)
    if generated_quiz_id:
        print("\n🎮 Testing Quiz Start...")
        try:
            response = requests.post(f"{BASE_URL}/api/quiz/{generated_quiz_id}/start", headers=headers)
            if response.status_code == 200:
                print("✅ Quiz start successful")
                session_result = response.json()
                session_token = session_result.get('session_token')
                print(f"   Session token: {session_token[:20]}...")
                
                # Test quiz submission with session
                print("\n📊 Testing Quiz Submission...")
                submission_data = {
                    "answers": [0, 1, 0],  # Sample answers
                    "time_taken": 120
                }
                
                response = requests.post(f"{BASE_URL}/api/quiz/session/{session_token}/submit", 
                                       json=submission_data, headers=headers)
                if response.status_code == 200:
                    print("✅ Quiz submission successful")
                    result = response.json()
                    print(f"   Score: {result.get('score')}%")
                    print(f"   Correct answers: {result.get('correct_answers')}/{result.get('total_questions')}")
                else:
                    print(f"⚠️ Quiz submission: {response.status_code} - {response.text}")
            else:
                print(f"⚠️ Quiz start: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Quiz start/submission error: {e}")
    
    # Test get user results
    print("\n� Testing Get User Results...")
    try:
        response = requests.get(f"{BASE_URL}/api/my-results", headers=headers)
        if response.status_code == 200:
            print("✅ Get results successful")
            results = response.json()
            print(f"   Total attempts: {len(results)}")
        else:
            print(f"⚠️ Get results: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Get results error: {e}")

def check_database_writes():
    """Check if data is being written to database by monitoring before/after states"""
    print("\n🔍 Checking Database Write Operations...")
    print("="*40)
    
    # Run the database inspection again to see current state
    import subprocess
    result = subprocess.run([
        "C:/Python313/python.exe", "-c",
        """
import sqlite3
conn = sqlite3.connect('backend/instance/quizgenix.db')
cursor = conn.cursor()

# Get current counts
cursor.execute('SELECT COUNT(*) FROM user')
users = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM quiz')
quizzes = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM quiz_attempt')
attempts = cursor.fetchone()[0]

print(f'Current Database State:')
print(f'  Users: {users}')
print(f'  Quizzes: {quizzes}')
print(f'  Quiz Attempts: {attempts}')

conn.close()
        """
    ], capture_output=True, text=True, cwd="c:\\Projects\\Quizgenix\\Quizgenix")
    
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")

if __name__ == "__main__":
    print(f"⏰ API Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_api_endpoints()
    check_database_writes()
    
    print("\n✨ API testing complete!")
    print("\n💡 Recommendations:")
    print("   1. Check that both frontend (port 3000) and backend (port 5000) are running")
    print("   2. Try creating a quiz through the web interface")
    print("   3. Monitor the database_export.json file for data changes")
    print("   4. Check browser developer tools for API call logs")

# 🧪 Quizgenix Testing Guide

This comprehensive guide will help you test all the functionality in your Quizgenix application.

## 🚀 Getting Started

### Prerequisites
1. **Backend running**: Make sure your Flask backend is running on `http://127.0.0.1:5000`
2. **Frontend running**: Make sure your React frontend is running on `http://localhost:3000`

### Quick Start
```bash
# Terminal 1 - Backend
cd backend/app
python main.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

## 🔐 Authentication Testing

### 1. Registration Testing
**Steps:**
1. Navigate to `http://localhost:3000`
2. Click "Sign Up" tab
3. Fill out the registration form:
   - **Name**: John Doe
   - **Email**: john@example.com
   - **Password**: password123
   - **Confirm Password**: password123
   - **Role**: Student (or Lecturer)
4. Click "Sign Up"

**Expected Result:**
- User should be registered and automatically logged in
- Should redirect to dashboard based on role

### 2. Login Testing
**Steps:**
1. If logged in, logout first
2. Click "Login" tab
3. Enter credentials:
   - **Email**: john@example.com
   - **Password**: password123
4. Click "Login"

**Expected Result:**
- User should be logged in and redirected to role-based dashboard

### 3. Role-Based Access Testing
**Test different roles:**
- **Student**: Should see "Take Quiz", "Available Quizzes", "Completed", "My Results" tabs
- **Lecturer**: Should see "Create Quiz", "My Quizzes", "Students", "Grades" tabs

## 👨‍🏫 Lecturer Dashboard Testing

### 1. Create Quiz Tab
**Steps:**
1. Login as a lecturer
2. Go to "Create Quiz" tab
3. Fill out the form:
   - **Topic**: Mathematics
   - **Number of Questions**: 5
   - **Difficulty**: Medium
   - **Time Limit**: 30 minutes
4. Click "Generate Quiz"

**Expected Result:**
- Should show success message
- Quiz should be generated and stored
- Form should reset

**Test Different Topics:**
- Science
- History
- Geography
- Programming
- Literature

### 2. My Quizzes Tab
**Steps:**
1. Go to "My Quizzes" tab
2. View created quizzes
3. Test download buttons:
   - Click "📄 PDF" button
   - Click "📘 Word" button
4. Click "🔗 Share" button

**Expected Result:**
- Should display list of created quizzes
- Download buttons should trigger file downloads
- Share button should show share functionality

### 3. Students Tab
**Steps:**
1. Go to "Students" tab
2. View registered students
3. Check student information display

**Expected Result:**
- Should show list of registered students
- Display student names, emails, and stats
- Show avatar with first letter of name

### 4. Grades Tab
**Steps:**
1. Go to "Grades" tab
2. View student grades table
3. Test download buttons:
   - Click "📊 Excel" button
   - Click "📋 CSV" button
4. Click "👁️ View" buttons on individual grades

**Expected Result:**
- Should display grades in table format
- Download buttons should work
- View buttons should show grade details

## 👨‍🎓 Student Dashboard Testing

### 1. Take Quiz Tab
**Steps:**
1. Login as a student
2. Go to "Take Quiz" tab (should be default)
3. Click "Create Custom Quiz" button

**Expected Result:**
- Should navigate to quiz creation interface
- Should show topic selector

### 2. Available Quizzes Tab
**Steps:**
1. Go to "Available Quizzes" tab
2. View available quizzes
3. Click "Start Quiz" on any quiz

**Expected Result:**
- Should display available quizzes
- Start Quiz button should work
- Should show quiz metadata (difficulty, creator, etc.)

### 3. Completed Tab
**Steps:**
1. Go to "Completed" tab
2. View completed quizzes
3. Click "View Details" on completed quizzes

**Expected Result:**
- Should show completed quiz history
- Display scores and completion dates
- View Details should show detailed results

### 4. My Results Tab
**Steps:**
1. Go to "My Results" tab
2. View statistics cards
3. Check results table
4. Click action buttons ("📄 View", "🔄 Retake")

**Expected Result:**
- Should display personal statistics
- Show performance by subject
- Action buttons should be functional

## 🧠 Quiz Flow Testing

### 1. Complete Quiz Creation Flow
**Steps:**
1. Login as lecturer
2. Create a quiz with specific topic
3. Logout and login as student
4. Take the created quiz
5. Complete the quiz
6. View results
7. Logout and login as lecturer
8. Check grades tab for student results

### 2. Quiz Taking Experience
**Steps:**
1. Start a quiz from student dashboard
2. Answer questions
3. Test navigation (if available)
4. Submit quiz
5. View scorecard
6. Test "Back to Dashboard" button

## 🔄 Navigation Testing

### 1. Dashboard Navigation
**Test all navigation elements:**
- Tab switching
- Logout functionality
- Back to dashboard buttons
- Role-based tab visibility

### 2. Authentication Flow
**Test navigation between:**
- Login ↔ Register tabs
- Login → Dashboard
- Dashboard → Logout → Login

## 📱 Responsive Design Testing

### 1. Mobile Testing
**Test on different screen sizes:**
- Mobile (320px - 768px)
- Tablet (768px - 1024px)
- Desktop (1024px+)

**Elements to test:**
- Login form layout
- Dashboard tabs
- Tables and grids
- Button layouts

## 🔍 Error Handling Testing

### 1. Authentication Errors
**Test scenarios:**
- Wrong password
- Non-existent email
- Network errors
- Server down

### 2. Quiz Generation Errors
**Test scenarios:**
- Invalid topics
- Network timeouts
- API failures

### 3. Form Validation
**Test scenarios:**
- Empty required fields
- Invalid email formats
- Password mismatches
- Character limits

## 🎨 UI/UX Testing

### 1. Animation Testing
**Elements to test:**
- Login card animations
- Floating shapes
- Button hover effects
- Tab transitions
- Loading spinners

### 2. Visual Feedback
**Test scenarios:**
- Loading states
- Success messages
- Error alerts
- Hover effects
- Focus states

## ⚡ Performance Testing

### 1. Load Times
**Test scenarios:**
- Initial page load
- Dashboard switching
- Quiz generation
- Large data tables

### 2. Memory Usage
**Monitor:**
- Browser memory consumption
- React component re-renders
- API response times

## 🔧 Browser Compatibility Testing

### Test on different browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Test features:
- CSS animations
- Fetch API calls
- LocalStorage
- Form submissions

## 📊 Backend API Testing

### 1. Authentication Endpoints
```bash
# Register
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123","role":"student"}'

# Login
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 2. Quiz Endpoints
```bash
# Generate Quiz (requires auth token)
curl -X POST http://127.0.0.1:5000/api/quiz \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"topic":"Mathematics","num_questions":5}'

# Submit Score
curl -X POST http://127.0.0.1:5000/api/score \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"questions":[],"user_answers":[],"topic":"Mathematics"}'
```

## 🐛 Common Issues & Solutions

### Issue: "Token is missing" error
**Solution:** Make sure you're logged in and the token is stored in localStorage

### Issue: CORS errors
**Solution:** Check that Flask-CORS is enabled in backend

### Issue: Quiz generation fails
**Solution:** Check backend logs and ensure API keys are configured

### Issue: Animations not working
**Solution:** Ensure CSS files are properly loaded and browser supports animations

## ✅ Testing Checklist

### Authentication
- [ ] User registration works
- [ ] User login works
- [ ] Logout functionality works
- [ ] Role-based access control works
- [ ] Token persistence works

### Lecturer Features
- [ ] Quiz creation works
- [ ] Quiz list displays correctly
- [ ] Student list shows data
- [ ] Grades table functions
- [ ] Download buttons work

### Student Features
- [ ] Quiz taking interface works
- [ ] Available quizzes display
- [ ] Completed quizzes show
- [ ] Results statistics work
- [ ] Navigation between tabs works

### UI/UX
- [ ] Animations work smoothly
- [ ] Responsive design works
- [ ] Loading states display
- [ ] Error handling works
- [ ] Visual feedback is clear

### Technical
- [ ] API calls succeed
- [ ] Data persistence works
- [ ] Cross-browser compatibility
- [ ] Performance is acceptable
- [ ] No console errors

## 🎯 Success Criteria

Your Quizgenix application is fully functional when:

1. **Authentication flows work seamlessly**
2. **Both lecturer and student dashboards are fully functional**
3. **Quiz creation and taking works end-to-end**
4. **All buttons and navigation work as expected**
5. **UI animations and responsive design work properly**
6. **No major console errors or broken functionality**

## 📞 Need Help?

If you encounter any issues during testing:

1. **Check browser console** for JavaScript errors
2. **Check backend terminal** for Python errors
3. **Verify API endpoints** are responding
4. **Test with different data** to isolate issues
5. **Try different browsers** to rule out compatibility issues

Happy Testing! 🚀

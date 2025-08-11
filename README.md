# 🎯 Quizgenix - AI-Powered Quiz Generation Platform

> **Advanced AI-driven quiz platform with real-time quiz taking, reference verification, and comprehensive analytics**

![Quizgenix Banner](https://img.shields.io/badge/Quizgenix-AI%20Powered-blue?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-3.13-green?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18.0-blue?style=for-the-badge&logo=react)
![Flask](https://img.shields.io/badge/Flask-3.0-red?style=for-the-badge&logo=flask)
![GitHub Stars](https://img.shields.io/github/stars/JanetArockya/Quizgenix?style=for-the-badge)
![GitHub Forks](https://img.shields.io/github/forks/JanetArockya/Quizgenix?style=for-the-badge)
![GitHub Issues](https://img.shields.io/github/issues/JanetArockya/Quizgenix?style=for-the-badge)

## ✨ Features

### 🤖 **AI-Powered Question Generation**
- **Smart Knowledge Base**: 4 domains (JavaScript, Python, Mathematics, Science)
- **Contextual Questions**: Questions adapt to topic and difficulty
- **Reference Verification**: Authoritative sources for each answer
- **Logical Answer Distribution**: Randomized correct answers

### 📝 **Interactive Quiz Taking**
- **Real-time Sessions**: Secure, timed quiz sessions
- **Progress Tracking**: Visual progress bars and question indicators
- **Auto-save Answers**: Answers saved as students progress
- **Auto-submit**: Quiz submits when time runs out
- **Detailed Results**: Explanations and references for learning

### 📊 **Advanced Analytics**
- **Performance Tracking**: Student progress monitoring
- **Quiz Statistics**: Completion rates and score analysis
- **Detailed Reports**: Export analytics in multiple formats

### 📁 **Multi-format Export**
- **PDF Generation**: Professional quiz documents
- **Word Documents**: Editable .docx files
- **Excel Spreadsheets**: Data analysis ready .xlsx files

### 🔐 **Security & Authentication**
- **JWT Authentication**: Secure token-based auth
- **Role-based Access**: Lecturer and Student roles
- **Session Management**: Secure quiz sessions

## 🛠️ **Tech Stack**

### **Backend**
- **Python 3.13** - Core backend language
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **JWT** - Authentication tokens
- **FPDF2** - PDF generation
- **python-docx** - Word document generation
- **pandas** - Excel file generation

### **Frontend**
- **React 18** - Frontend framework
- **Modern CSS** - Responsive design
- **Fetch API** - HTTP client

### **Database**
- **SQLite** - Development database
- **PostgreSQL ready** - Production database support

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.13+
- Node.js 18+
- npm or yarn

### **Backend Setup**
```bash
# Clone repository
git clone https://github.com/JanetArockya/Quizgenix.git
cd Quizgenix/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python app/main.py
```

### **Frontend Setup**
```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Start development server
npm start
```

### **Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

### **Test Accounts**
- **Lecturer**: `lecturer@test.com` / `password123`
- **Student**: `student@test.com` / `password123`

## 📊 **API Endpoints**

### **Authentication**
- `POST /api/login` - User login
- `POST /api/register` - User registration

### **Quiz Management**
- `POST /api/quiz` - Create new quiz
- `GET /api/quizzes` - Get user's quizzes
- `GET /api/quiz/<id>/download/<format>` - Download quiz

### **Quiz Taking**
- `POST /api/quiz/<id>/start` - Start quiz session
- `POST /api/quiz/session/<token>/answer` - Submit answer
- `POST /api/quiz/session/<token>/submit` - Submit quiz

### **Analytics**
- `GET /api/quiz/<id>/attempts` - Get quiz attempts
- `GET /api/my-results` - Get student results

## 🎯 **Project Structure**

```
Quizgenix/
├── backend/
│   ├── app/
│   │   ├── main.py          # Main Flask application
│   │   └── file_service.py  # File generation services
│   ├── models/
│   │   └── quiz_model.py    # Database models
│   ├── requirements.txt     # Python dependencies
│   └── .env                # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js     # Main dashboard
│   │   │   ├── Login.js         # Authentication
│   │   │   ├── QuizTaking.js    # Quiz interface
│   │   │   └── *.css           # Component styles
│   │   ├── App.js          # Main app component
│   │   └── index.js        # App entry point
│   ├── package.json        # Node dependencies
│   └── public/            # Static assets
└── README.md              # Project documentation
```

## 🔧 **Configuration**

### **Environment Variables**
Create `.env` files in both backend and frontend directories:

**Backend (.env):**
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///quizgenix.db
FLASK_ENV=development
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:5000
```

## 🚀 **Features in Development**

### **Phase 2: Analytics Dashboard**
- [ ] Performance visualization
- [ ] Learning progress tracking
- [ ] Comparative analytics
- [ ] Advanced reporting

### **Phase 3: User Management**
- [ ] Student groups/classes
- [ ] Bulk student import
- [ ] Quiz sharing between lecturers
- [ ] Advanced permissions

### **Phase 4: AI Enhancements**
- [ ] Personalized question generation
- [ ] Adaptive difficulty
- [ ] Learning recommendations
- [ ] Question quality scoring

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 **Author**

**Janet Arockya**
- GitHub: [@JanetArockya](https://github.com/JanetArockya)
- Repository: [Quizgenix](https://github.com/JanetArockya/Quizgenix)

## 🏆 **Project Highlights**

- ✅ **AI-Powered**: Advanced question generation with 4 knowledge domains
- ✅ **Real-time**: Interactive quiz taking with live progress tracking
- ✅ **Verified**: Authoritative references for answer verification
- ✅ **Responsive**: Mobile-first design with modern UI
- ✅ **Secure**: JWT authentication with role-based access
- ✅ **Exportable**: Multiple file formats (PDF, Word, Excel)

## 🎉 **Acknowledgments**

- **MDN Web Docs** - JavaScript references
- **Python.org** - Python documentation  
- **Khan Academy** - Educational content structure
- **React Team** - Frontend framework
- **Flask Team** - Backend framework

## 📈 **Stats**

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=JanetArockya&show_icons=true&theme=radical)

---

<div align="center">

**Made with ❤️ and lots of ☕ by Janet Arockya**

[⭐ Star this repo](https://github.com/JanetArockya/Quizgenix) • [🐛 Report Bug](https://github.com/JanetArockya/Quizgenix/issues) • [✨ Request Feature](https://github.com/JanetArockya/Quizgenix/issues)

**[🚀 Live Demo](https://github.com/JanetArockya/Quizgenix) | [📖 Documentation](https://github.com/JanetArockya/Quizgenix/wiki) | [💬 Discussions](https://github.com/JanetArockya/Quizgenix/discussions)**

</div>

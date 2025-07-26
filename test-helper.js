#!/usr/bin/env node

/**
 * Quizgenix Manual Testing Script
 * This script provides step-by-step testing instructions
 */

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

function showHeader() {
  console.clear();
  console.log(colorize('🧠 QUIZGENIX TESTING HELPER', 'cyan'));
  console.log(colorize('═'.repeat(50), 'blue'));
  console.log();
}

async function askQuestion(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer.toLowerCase().trim());
    });
  });
}

async function testSection(title, tests) {
  showHeader();
  console.log(colorize(`📋 ${title}`, 'yellow'));
  console.log('─'.repeat(30));
  console.log();

  for (let i = 0; i < tests.length; i++) {
    const test = tests[i];
    console.log(colorize(`Test ${i + 1}: ${test.name}`, 'bright'));
    console.log(`📝 ${test.description}`);
    console.log();
    
    if (test.steps) {
      console.log(colorize('Steps:', 'blue'));
      test.steps.forEach((step, index) => {
        console.log(`  ${index + 1}. ${step}`);
      });
      console.log();
    }

    if (test.expected) {
      console.log(colorize('Expected Result:', 'green'));
      console.log(`  ✅ ${test.expected}`);
      console.log();
    }

    const result = await askQuestion(colorize('Did this test pass? (y/n/skip): ', 'magenta'));
    
    if (result === 'n') {
      console.log(colorize('❌ Test failed. Please check the implementation.', 'red'));
      const details = await askQuestion('Enter details about the failure (optional): ');
      if (details) {
        console.log(colorize(`📝 Failure details: ${details}`, 'red'));
      }
    } else if (result === 'y') {
      console.log(colorize('✅ Test passed!', 'green'));
    } else {
      console.log(colorize('⏭️  Test skipped.', 'yellow'));
    }
    
    console.log();
    await askQuestion('Press Enter to continue...');
  }
}

async function runTests() {
  showHeader();
  console.log(colorize('Welcome to the Quizgenix Testing Helper!', 'bright'));
  console.log('This script will guide you through testing all functionality.');
  console.log();
  await askQuestion('Press Enter to start testing...');

  // Authentication Tests
  await testSection('AUTHENTICATION TESTING', [
    {
      name: 'User Registration',
      description: 'Test user registration with both student and lecturer roles',
      steps: [
        'Navigate to http://localhost:3000',
        'Click "Sign Up" tab',
        'Fill form: Name="John Doe", Email="john@example.com", Password="password123", Role="Student"',
        'Click "Sign Up" button'
      ],
      expected: 'User registered successfully and redirected to student dashboard'
    },
    {
      name: 'User Login',
      description: 'Test user login functionality',
      steps: [
        'Logout if logged in',
        'Click "Login" tab',
        'Enter: Email="john@example.com", Password="password123"',
        'Click "Login" button'
      ],
      expected: 'User logged in and redirected to dashboard'
    },
    {
      name: 'Logout Functionality',
      description: 'Test logout button',
      steps: [
        'Click the logout button in the dashboard header',
        'Verify redirection to login page'
      ],
      expected: 'User logged out and redirected to login page'
    }
  ]);

  // Lecturer Dashboard Tests
  await testSection('LECTURER DASHBOARD TESTING', [
    {
      name: 'Create Quiz Form',
      description: 'Test quiz creation functionality',
      steps: [
        'Login as lecturer (register with role="lecturer")',
        'Go to "Create Quiz" tab',
        'Fill: Topic="Mathematics", Questions=5, Difficulty="Medium", Time=30',
        'Click "Generate Quiz" button'
      ],
      expected: 'Quiz created successfully with success message'
    },
    {
      name: 'My Quizzes Tab',
      description: 'Test quiz listing and download buttons',
      steps: [
        'Go to "My Quizzes" tab',
        'Check if created quizzes are displayed',
        'Click "📄 PDF" button',
        'Click "📘 Word" button'
      ],
      expected: 'Quizzes displayed, download buttons trigger downloads'
    },
    {
      name: 'Students Tab',
      description: 'Test student listing',
      steps: [
        'Go to "Students" tab',
        'Check student information display'
      ],
      expected: 'Students listed with names, emails, and stats'
    },
    {
      name: 'Grades Tab',
      description: 'Test grades display and export',
      steps: [
        'Go to "Grades" tab',
        'Check grades table',
        'Click "📊 Excel" button',
        'Click "📋 CSV" button',
        'Click "👁️ View" button on a grade'
      ],
      expected: 'Grades displayed in table, export buttons work, view shows details'
    }
  ]);

  // Student Dashboard Tests
  await testSection('STUDENT DASHBOARD TESTING', [
    {
      name: 'Take Quiz Tab',
      description: 'Test custom quiz creation button',
      steps: [
        'Login as student',
        'Go to "Take Quiz" tab (should be default)',
        'Click "Create Custom Quiz" button'
      ],
      expected: 'Navigates to quiz interface with topic selector'
    },
    {
      name: 'Available Quizzes Tab',
      description: 'Test available quiz listing',
      steps: [
        'Go to "Available Quizzes" tab',
        'Check quiz listings',
        'Click "Start Quiz" button on any quiz'
      ],
      expected: 'Quizzes displayed with metadata, Start Quiz works'
    },
    {
      name: 'Completed Tab',
      description: 'Test completed quiz history',
      steps: [
        'Go to "Completed" tab',
        'Check completed quiz display',
        'Click "View Details" button'
      ],
      expected: 'Shows completed quizzes with scores and dates'
    },
    {
      name: 'My Results Tab',
      description: 'Test statistics and results table',
      steps: [
        'Go to "My Results" tab',
        'Check statistics cards',
        'Click "📄 View" button',
        'Click "🔄 Retake" button'
      ],
      expected: 'Statistics displayed, action buttons work'
    }
  ]);

  // UI/UX Tests
  await testSection('UI/UX TESTING', [
    {
      name: 'Animations and Transitions',
      description: 'Test visual animations',
      steps: [
        'Check login page floating shapes animation',
        'Test button hover effects',
        'Test tab switching animations',
        'Check loading spinner animations'
      ],
      expected: 'All animations work smoothly without glitches'
    },
    {
      name: 'Responsive Design',
      description: 'Test mobile responsiveness',
      steps: [
        'Resize browser window to mobile size (< 768px)',
        'Test navigation and forms',
        'Check table responsiveness',
        'Test button layouts'
      ],
      expected: 'Interface adapts properly to different screen sizes'
    },
    {
      name: 'Error Handling',
      description: 'Test error scenarios',
      steps: [
        'Try logging in with wrong password',
        'Try registering with existing email',
        'Test form validation (empty fields)',
        'Check network error handling'
      ],
      expected: 'Appropriate error messages displayed'
    }
  ]);

  // Integration Tests
  await testSection('INTEGRATION TESTING', [
    {
      name: 'Complete Quiz Flow',
      description: 'Test end-to-end quiz workflow',
      steps: [
        'Login as lecturer and create a quiz',
        'Logout and login as student',
        'Find and start the created quiz',
        'Complete the quiz and view results',
        'Logout and login as lecturer',
        'Check grades tab for student results'
      ],
      expected: 'Complete workflow works from creation to grading'
    },
    {
      name: 'Cross-Role Functionality',
      description: 'Test role-based access',
      steps: [
        'Test that students cannot access lecturer features',
        'Test that lecturers cannot access student-only features',
        'Verify role-based tab visibility'
      ],
      expected: 'Role-based access control works properly'
    }
  ]);

  showHeader();
  console.log(colorize('🎉 TESTING COMPLETE!', 'green'));
  console.log();
  console.log('Your Quizgenix application has been thoroughly tested.');
  console.log('If all tests passed, your application is fully functional!');
  console.log();
  console.log(colorize('Next Steps:', 'cyan'));
  console.log('1. Fix any failing tests');
  console.log('2. Re-run specific test sections');
  console.log('3. Deploy your application');
  console.log();

  rl.close();
}

// Run the testing script
runTests().catch(console.error);

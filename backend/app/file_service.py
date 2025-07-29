import os
import json
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import tempfile

class QuizFileGenerator:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def generate_word_file(self, quiz_data):
        """Generate Word document with quiz questions"""
        doc = Document()
        
        # Title
        title = doc.add_heading(f"Quiz: {quiz_data.get('title', 'Untitled Quiz')}", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Quiz details section
        details_para = doc.add_paragraph()
        details_para.add_run("Quiz Details").bold = True
        details_para.add_run("\n" + "="*50)
        
        doc.add_paragraph(f"📚 Subject: {quiz_data.get('subject', 'N/A')}")
        doc.add_paragraph(f"🎯 Difficulty: {quiz_data.get('difficulty', 'N/A')}")
        doc.add_paragraph(f"📊 Total Questions: {len(quiz_data.get('questions', []))}")
        doc.add_paragraph(f"⏰ Estimated Time: {len(quiz_data.get('questions', [])) * 2} minutes")
        
        doc.add_paragraph("\n" + "="*50 + "\n")
        
        # Instructions
        instructions = doc.add_paragraph()
        instructions.add_run("Instructions:").bold = True
        doc.add_paragraph("• Read each question carefully")
        doc.add_paragraph("• Choose the best answer from the given options")
        doc.add_paragraph("• Mark your answers clearly")
        doc.add_paragraph("• Review your answers before submission")
        
        doc.add_paragraph("\n" + "="*50 + "\n")
        
        # Questions
        for i, question in enumerate(quiz_data.get('questions', []), 1):
            # Question text
            question_para = doc.add_paragraph()
            question_para.add_run(f"Question {i}: ").bold = True
            question_para.add_run(question.get('question', ''))
            
            # Options
            options = question.get('options', [])
            for j, option in enumerate(options):
                option_letter = chr(65 + j)  # A, B, C, D
                option_para = doc.add_paragraph(f"   {option_letter}) {option}")
                option_para.style = 'List Bullet'
            
            # Answer space
            doc.add_paragraph("Answer: _____")
            doc.add_paragraph()  # Add space between questions
        
        # Answer key section
        doc.add_page_break()
        answer_title = doc.add_heading("Answer Key", level=1)
        answer_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        for i, question in enumerate(quiz_data.get('questions', []), 1):
            correct_answer = question.get('correct_answer', '')
            # Find the option letter for the correct answer
            options = question.get('options', [])
            answer_letter = 'N/A'
            for j, option in enumerate(options):
                if option == correct_answer:
                    answer_letter = chr(65 + j)
                    break
            
            answer_para = doc.add_paragraph()
            answer_para.add_run(f"Question {i}: ").bold = True
            answer_para.add_run(f"{answer_letter}) {correct_answer}")
        
        # Save to temporary file
        filename = f"quiz_{quiz_data.get('id', 'temp')}_{quiz_data.get('title', 'quiz').replace(' ', '_')}.docx"
        filepath = os.path.join(self.temp_dir, filename)
        doc.save(filepath)
        
        return filepath, filename
    
    def generate_pdf_file(self, quiz_data):
        """Generate PDF document with quiz questions"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 20)
        
        # Title
        title = quiz_data.get('title', 'Untitled Quiz')
        pdf.cell(0, 15, f'Quiz: {title}', 0, 1, 'C')
        pdf.ln(5)
        
        # Quiz details
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Quiz Details', 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, '='*80, 0, 1)
        
        pdf.cell(0, 6, f"Subject: {quiz_data.get('subject', 'N/A')}", 0, 1)
        pdf.cell(0, 6, f"Difficulty: {quiz_data.get('difficulty', 'N/A')}", 0, 1)
        pdf.cell(0, 6, f"Total Questions: {len(quiz_data.get('questions', []))}", 0, 1)
        pdf.cell(0, 6, f"Estimated Time: {len(quiz_data.get('questions', [])) * 2} minutes", 0, 1)
        pdf.ln(3)
        
        # Instructions
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Instructions:', 0, 1)
        pdf.set_font('Arial', '', 10)
        instructions = [
            "• Read each question carefully",
            "• Choose the best answer from the given options", 
            "• Mark your answers clearly",
            "• Review your answers before submission"
        ]
        for instruction in instructions:
            pdf.cell(0, 6, instruction.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
        
        pdf.ln(5)
        pdf.cell(0, 5, '='*80, 0, 1)
        pdf.ln(5)
        
        # Questions
        for i, question in enumerate(quiz_data.get('questions', []), 1):
            # Check if we need a new page
            if pdf.get_y() > 250:
                pdf.add_page()
            
            # Question text
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, f"Question {i}:", 0, 1)
            
            pdf.set_font('Arial', '', 11)
            question_text = question.get('question', '')
            # Handle long questions by wrapping text
            if len(question_text) > 85:
                lines = [question_text[i:i+85] for i in range(0, len(question_text), 85)]
                for line in lines:
                    pdf.cell(0, 6, line.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
            else:
                pdf.cell(0, 6, question_text.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
            
            pdf.ln(2)
            
            # Options
            options = question.get('options', [])
            for j, option in enumerate(options):
                option_letter = chr(65 + j)  # A, B, C, D
                option_text = f"   {option_letter}) {option}"
                pdf.cell(0, 6, option_text.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
            
            pdf.ln(2)
            pdf.cell(0, 6, "Answer: _____", 0, 1)
            pdf.ln(6)
        
        # Answer key on new page
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 12, 'Answer Key', 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        for i, question in enumerate(quiz_data.get('questions', []), 1):
            correct_answer = question.get('correct_answer', '')
            options = question.get('options', [])
            answer_letter = 'N/A'
            for j, option in enumerate(options):
                if option == correct_answer:
                    answer_letter = chr(65 + j)
                    break
            
            answer_text = f"Question {i}: {answer_letter}) {correct_answer}"
            pdf.cell(0, 6, answer_text.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
        
        # Save to temporary file
        filename = f"quiz_{quiz_data.get('id', 'temp')}_{quiz_data.get('title', 'quiz').replace(' ', '_')}.pdf"
        filepath = os.path.join(self.temp_dir, filename)
        pdf.output(filepath)
        
        return filepath, filename

    def generate_excel_file(self, quiz_data):
        """Generate Excel file with quiz questions"""
        try:
            import pandas as pd
            
            # Prepare data for Excel
            questions_data = []
            for i, question in enumerate(quiz_data.get('questions', []), 1):
                options = question.get('options', [])
                questions_data.append({
                    'Question_No': i,
                    'Question': question.get('question', ''),
                    'Option_A': options[0] if len(options) > 0 else '',
                    'Option_B': options[1] if len(options) > 1 else '',
                    'Option_C': options[2] if len(options) > 2 else '',
                    'Option_D': options[3] if len(options) > 3 else '',
                    'Correct_Answer': question.get('correct_answer', ''),
                    'Subject': quiz_data.get('subject', ''),
                    'Difficulty': quiz_data.get('difficulty', ''),
                    'Quiz_Title': quiz_data.get('title', '')
                })
            
            df = pd.DataFrame(questions_data)
            
            # Save to temporary file
            filename = f"quiz_{quiz_data.get('id', 'temp')}_{quiz_data.get('title', 'quiz').replace(' ', '_')}.xlsx"
            filepath = os.path.join(self.temp_dir, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Quiz Questions', index=False)
                
                # Add quiz info sheet
                quiz_info = pd.DataFrame([
                    ['Quiz Title', quiz_data.get('title', 'N/A')],
                    ['Subject', quiz_data.get('subject', 'N/A')],
                    ['Difficulty', quiz_data.get('difficulty', 'N/A')],
                    ['Total Questions', len(quiz_data.get('questions', []))],
                    ['Estimated Time (minutes)', len(quiz_data.get('questions', [])) * 2],
                    ['Created Date', quiz_data.get('created_at', 'N/A')]
                ], columns=['Property', 'Value'])
                
                quiz_info.to_excel(writer, sheet_name='Quiz Info', index=False)
            
            return filepath, filename
            
        except ImportError:
            return None, None
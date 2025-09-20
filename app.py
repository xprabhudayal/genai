import os
import PyPDF2
import docx
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import openai
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from config import get_config

# Load environment variables
load_dotenv()

# Get configuration
config = get_config()

app = Flask(__name__)
app.config.from_object(config)


# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenAI configuration
openai.api_key = app.config['OPENAI_API_KEY']
llm = ChatOpenAI(
    model=app.config['OPENAI_MODEL'],
    temperature=app.config['OPENAI_TEMPERATURE'],
    api_key=app.config['OPENAI_API_KEY']
)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading DOCX: {str(e)}")

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        raise ValueError(f"Error reading TXT: {str(e)}")

def extract_text_from_file(file_path, file_extension):
    """Extract text based on file extension"""
    if file_extension.lower() == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension.lower() == 'docx':
        return extract_text_from_docx(file_path)
    elif file_extension.lower() == 'txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format")

def simplify_legal_text(text):
    """Use AI to simplify legal text"""
    try:
        system_prompt = app.config['SIMPLIFICATION_PROMPT']
        
        human_prompt = f"Please simplify this legal text:\n\n{text[:4000]}"  # Limit text length
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error processing text with AI: {str(e)}"

def explain_legal_term(term):
    """Use AI to explain a legal term"""
    try:
        system_prompt = app.config['TERM_EXPLANATION_PROMPT']
        
        human_prompt = f"Please explain this legal term: {term}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error explaining term: {str(e)}"

def generate_document_summary(text):
    """Use AI to generate a document summary"""
    try:
        system_prompt = app.config['SUMMARY_PROMPT']
        
        human_prompt = f"Please summarize this legal document:\n\n{text[:3000]}"  # Limit text length
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Extract text from file
            file_extension = filename.rsplit('.', 1)[1].lower()
            extracted_text = extract_text_from_file(file_path, file_extension)
            
            # Process with AI
            simplified_text = simplify_legal_text(extracted_text)
            summary = generate_document_summary(extracted_text)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'original_text': extracted_text,
                'simplified_text': simplified_text,
                'summary': summary,
                'filename': filename
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/simplify', methods=['POST'])
def simplify_text():
    """Simplify legal text"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    simplified = simplify_legal_text(text)
    
    return jsonify({
        'success': True,
        'simplified_text': simplified
    })

@app.route('/explain', methods=['POST'])
def explain_term():
    """Explain a legal term"""
    data = request.get_json()
    if not data or 'term' not in data:
        return jsonify({'error': 'No term provided'}), 400
    
    term = data['term']
    explanation = explain_legal_term(term)
    
    return jsonify({
        'success': True,
        'explanation': explanation
    })

@app.route('/summarize', methods=['POST'])
def summarize_document():
    """Generate document summary"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    summary = generate_document_summary(text)
    
    return jsonify({
        'success': True,
        'summary': summary
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Legal Document AI Simplifier is running'})

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true', host='0.0.0.0', port=5000)

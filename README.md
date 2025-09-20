# Legal Document AI Simplifier

## Problem Statement
Legal documents are often written in complex, technical language that makes them inaccessible to the general public. This creates a barrier to understanding legal rights, obligations, and processes.

## Solution
An AI-powered web application that:
- **Simplifies Legal Language**: Converts complex legal jargon into plain English
- **Explains Legal Terms**: Provides definitions and examples for legal terminology
- **Generates Summaries**: Creates concise summaries of legal documents
- **Interactive Interface**: User-friendly web interface for document upload and analysis

## Features
- 📄 **Multi-format Support**: PDF, DOCX, and plain text documents
- 🤖 **AI-Powered Analysis**: Uses OpenAI's GPT models for intelligent document processing
- 📝 **Smart Summarization**: Generates easy-to-understand summaries
- 🔍 **Term Explanation**: Interactive tooltips for legal terms
- 💡 **Plain English Translation**: Converts legal language to everyday speech
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Technology Stack
- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenAI GPT models via LangChain
- **Document Processing**: PyPDF2, python-docx
- **UI Framework**: Streamlit (alternative interface)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd legal-document-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

4. Run the application:
```bash
# Flask version
python app.py

# Streamlit version
streamlit run streamlit_app.py
```

## Usage

1. **Upload Document**: Drag and drop or select a legal document
2. **AI Processing**: The system analyzes the document using AI
3. **View Results**: See simplified text, explanations, and summary
4. **Interactive Features**: Click on terms for detailed explanations

## API Endpoints

- `POST /upload` - Upload and process documents
- `GET /simplify` - Simplify legal text
- `GET /explain` - Get term explanations
- `GET /summarize` - Generate document summary

## Contributing
Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License
MIT License - see LICENSE file for details.

## Support
For support and questions, please open an issue in the repository.

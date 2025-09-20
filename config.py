"""
Configuration file for Legal Document AI Simplifier
Customize these settings to match your needs
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_BASE_URL = os.getenv('OPENAI_API_BASE_URL')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.3))
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = '0.0.0.0'
    PORT = 5000
    
    # File Upload Configuration
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,txt').split(',')
    
    # AI Processing Configuration
    MAX_TEXT_LENGTH = 4000  # Maximum characters for AI processing
    MAX_SUMMARY_LENGTH = 3000  # Maximum characters for summary generation
    
    # UI Configuration
    APP_NAME = "Legal Document AI Simplifier"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Demystifying Legal Documents with AI"
    
    # Feature Flags
    ENABLE_FILE_UPLOAD = True
    ENABLE_TEXT_INPUT = True
    ENABLE_TERM_EXPLORER = True
    ENABLE_DOCUMENT_SUMMARY = True
    
    # Legal Term Patterns (for automatic detection)
    LEGAL_TERM_PATTERNS = [
        # Capitalized phrases
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-zA-Z]*)*\b',
        
        # Common legal words
        r'\b(?:hereby|whereas|hereinafter|aforesaid|pursuant|whereby|notwithstanding)\b',
        
        # Legal concepts
        r'\b(?:party|parties|agreement|contract|terms|conditions|liability|damages|breach|termination)\b',
        
        # Latin terms
        r'\b(?:prima facie|de facto|de jure|pro bono|ad hoc|ex parte|in camera|subpoena)\b',
        
        # Contract elements
        r'\b(?:consideration|offer|acceptance|capacity|legality|mutual assent|meeting of minds)\b'
    ]
    
    # Common Legal Terms for Quick Access
    COMMON_LEGAL_TERMS = [
        "Force Majeure",
        "Indemnification", 
        "Breach of Contract",
        "Liquidated Damages",
        "Arbitration",
        "Jurisdiction",
        "Statute of Limitations",
        "Consideration",
        "Due Diligence",
        "Material Adverse Effect",
        "Severability",
        "Waiver",
        "Covenant",
        "Representation",
        "Warranty",
        "Default",
        "Remedy",
        "Damages",
        "Specific Performance",
        "Injunction"
    ]
    
    # AI Prompt Templates
    SIMPLIFICATION_PROMPT = """You are a legal expert who specializes in making complex legal documents understandable to the general public. 
    Your task is to:
    1. Simplify complex legal language into plain English
    2. Maintain the legal meaning and accuracy
    3. Use clear, simple language that a high school student could understand
    4. Break down complex sentences into shorter, clearer ones
    5. Replace legal jargon with everyday language when possible
    
    Format your response as:
    - Simplified Text: [the simplified version]
    - Key Terms Explained: [list and explain important legal terms]
    - Summary: [2-3 sentence summary of the main points]"""
    
    TERM_EXPLANATION_PROMPT = """You are a legal expert who explains legal terms in simple, understandable language. 
    For each legal term, provide:
    1. A simple definition in plain English
    2. A practical example of how it's used
    3. Why it's important to understand
    
    Keep your explanation under 100 words and use everyday language."""
    
    SUMMARY_PROMPT = """You are a legal expert who creates clear, concise summaries of legal documents. 
    Create a summary that:
    1. Captures the main purpose and key points
    2. Identifies the most important legal implications
    3. Highlights any deadlines, requirements, or actions needed
    4. Uses simple, clear language
    
    Keep your summary under 200 words."""
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OpenAI API key is required")
        
        if cls.MAX_FILE_SIZE <= 0:
            errors.append("MAX_FILE_SIZE must be positive")
        
        if cls.OPENAI_TEMPERATURE < 0 or cls.OPENAI_TEMPERATURE > 1:
            errors.append("OPENAI_TEMPERATURE must be between 0 and 1")
        
        return errors
    
    @classmethod
    def get_upload_folder(cls):
        """Get upload folder path and create if it doesn't exist"""
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        return cls.UPLOAD_FOLDER

# Development configuration
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    OPENAI_MODEL = 'gpt-4'
    OPENAI_TEMPERATURE = 0.3

# Production configuration
class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    OPENAI_MODEL = 'gpt-4'
    OPENAI_TEMPERATURE = 0.1
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')  # Must be set in production

# Testing configuration
class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    OPENAI_API_KEY = 'test-key'
    OPENAI_MODEL = 'gpt-3.5-turbo'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])

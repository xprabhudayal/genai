#!/usr/bin/env python3
"""
Test script for Legal Document AI Simplifier
This script tests the basic functionality without requiring OpenAI API calls
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock OpenAI API key for testing
os.environ['OPENAI_API_KEY'] = 'test-key'

class TestLegalDocumentAI(unittest.TestCase):
    """Test cases for the Legal Document AI application"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_legal_text = """
        WHEREAS, Party A (hereinafter referred to as "the Company") and Party B (hereinafter referred to as "the Contractor") 
        desire to enter into a binding agreement for the provision of professional services;
        
        AND WHEREAS, the parties have agreed upon the terms and conditions set forth herein;
        
        NOW, THEREFORE, in consideration of the mutual promises and covenants contained herein, the parties agree as follows:
        
        1. SERVICES. The Contractor shall provide professional consulting services as described in Exhibit A.
        
        2. TERM. This Agreement shall commence on the Effective Date and continue for a period of twelve (12) months.
        
        3. COMPENSATION. The Company shall pay the Contractor a monthly fee of $5,000 for services rendered.
        
        4. TERMINATION. Either party may terminate this Agreement upon thirty (30) days written notice.
        
        5. CONFIDENTIALITY. The Contractor shall maintain the confidentiality of all proprietary information.
        
        6. GOVERNING LAW. This Agreement shall be governed by the laws of the State of California.
        """
        
        self.sample_legal_terms = [
            "force majeure",
            "indemnification", 
            "breach of contract",
            "liquidated damages",
            "arbitration"
        ]
    
    def test_file_extensions(self):
        """Test allowed file extensions"""
        from app import allowed_file
        
        self.assertTrue(allowed_file('document.pdf'))
        self.assertTrue(allowed_file('contract.docx'))
        self.assertTrue(allowed_file('agreement.txt'))
        self.assertFalse(allowed_file('document.doc'))
        self.assertFalse(allowed_file('image.jpg'))
    
    def test_text_extraction_pdf(self):
        """Test PDF text extraction (mocked)"""
        with patch('PyPDF2.PdfReader') as mock_pdf:
            mock_reader = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Sample PDF text"
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader
            
            from app import extract_text_from_pdf
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b"dummy pdf content")
                temp_file.flush()
                
                result = extract_text_from_pdf(temp_file.name)
                self.assertEqual(result, "Sample PDF text")
                
                # Clean up
                os.unlink(temp_file.name)
    
    def test_text_extraction_docx(self):
        """Test DOCX text extraction (mocked)"""
        with patch('docx.Document') as mock_docx:
            mock_document = MagicMock()
            mock_paragraph = MagicMock()
            mock_paragraph.text = "Sample DOCX text"
            mock_document.paragraphs = [mock_paragraph]
            mock_docx.return_value = mock_document
            
            from app import extract_text_from_docx
            
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(b"dummy docx content")
                temp_file.flush()
                
                result = extract_text_from_docx(temp_file.name)
                self.assertEqual(result, "Sample DOCX text")
                
                # Clean up
                os.unlink(temp_file.name)
    
    def test_text_extraction_txt(self):
        """Test TXT text extraction"""
        from app import extract_text_from_txt
        
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as temp_file:
            temp_file.write("Sample text file content")
            temp_file.flush()
            
            result = extract_text_from_txt(temp_file.name)
            self.assertEqual(result, "Sample text file content")
            
            # Clean up
            os.unlink(temp_file.name)
    
    def test_legal_term_extraction(self):
        """Test legal term extraction from JavaScript"""
        # This would test the JavaScript function extractLegalTerms
        # For now, we'll test the pattern matching logic
        import re
        
        text = self.sample_legal_text
        
        # Test capitalized phrases pattern
        capitalized_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(capitalized_pattern, text)
        
        self.assertIn("Party A", matches)
        self.assertIn("Party B", matches)
        self.assertIn("Effective Date", matches)
        
        # Test legal terms pattern
        legal_terms_pattern = r'\b(?:hereby|whereas|hereinafter|aforesaid|pursuant|whereby|notwithstanding)\b'
        legal_matches = re.findall(legal_terms_pattern, text, re.IGNORECASE)
        
        self.assertIn("WHEREAS", legal_matches)
        self.assertIn("hereinafter", legal_matches)
    
    def test_ai_prompt_structure(self):
        """Test AI prompt structure and formatting"""
        from app import app, simplify_legal_text, explain_legal_term, generate_document_summary
        
        with app.app_context():
            # Test that the prompts are well-structured
            self.assertIn("Simplify complex legal language", app.config['SIMPLIFICATION_PROMPT'])
            self.assertIn("explain legal terms", app.config['TERM_EXPLANATION_PROMPT'])
            self.assertIn("summaries of legal documents", app.config['SUMMARY_PROMPT'])

            # Mock the LLM response
            mock_response = MagicMock()
            mock_response.content = "Mock AI response"
            
            with patch('app.llm') as mock_llm:
                mock_llm.invoke.return_value = mock_response
                
                # Test simplification prompt
                result = simplify_legal_text("Test legal text")
                self.assertEqual(result, "Mock AI response")
                
                # Test term explanation prompt
                result = explain_legal_term("test term")
                self.assertEqual(result, "Mock AI response")
                
                # Test summary prompt
                result = generate_document_summary("Test document text")
                self.assertEqual(result, "Mock AI response")
    
    def test_error_handling(self):
        """Test error handling in various functions"""
        from app import extract_text_from_pdf, extract_text_from_docx
        
        # Test PDF error handling
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"invalid pdf content")
            temp_file.flush()
            
            with self.assertRaises(ValueError):
                extract_text_from_pdf(temp_file.name)
            
            # Clean up
            os.unlink(temp_file.name)
        
        # Test DOCX error handling
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_file.write(b"invalid docx content")
            temp_file.flush()
            
            with self.assertRaises(ValueError):
                extract_text_from_docx(temp_file.name)
            
            # Clean up
            os.unlink(temp_file.name)
    
    def test_upload_route(self):
        """Test the /upload route"""
        from app import app

        with app.test_client() as client:
            with patch('app.simplify_legal_text') as mock_simplify, \
                 patch('app.generate_document_summary') as mock_summarize:
                
                mock_simplify.return_value = "Simplified text"
                mock_summarize.return_value = "Summary"

                # Test with a valid file
                with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as temp_file:
                    temp_file.write("Sample text file content")
                    temp_file.flush()
                    temp_file_path = temp_file.name
                
                with open(temp_file_path, 'rb') as f:
                    data = {'file': (f, 'test.txt')}
                    response = client.post('/upload', data=data, content_type='multipart/form-data')
                
                self.assertEqual(response.status_code, 200)
                json_data = response.get_json()
                self.assertTrue(json_data['success'])
                self.assertEqual(json_data['simplified_text'], "Simplified text")
                self.assertEqual(json_data['summary'], "Summary")

                os.unlink(temp_file_path)

                # Test with an invalid file type
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_file.write(b"dummy image content")
                    temp_file.flush()
                    temp_file_path = temp_file.name

                with open(temp_file_path, 'rb') as f:
                    data = {'file': (f, 'test.jpg')}
                    response = client.post('/upload', data=data, content_type='multipart/form-data')
                
                self.assertEqual(response.status_code, 400)
                json_data = response.get_json()
                self.assertIn('Invalid file type', json_data['error'])

                os.unlink(temp_file_path)

def run_tests():
    """Run all tests"""
    print("🧪 Running Legal Document AI Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLegalDocumentAI)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

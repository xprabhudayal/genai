import streamlit as st
import os
import tempfile
import io
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app import extract_text_from_file, simplify_legal_text, explain_legal_term, generate_document_summary
from config import get_config

# Load environment variables
load_dotenv()

# Get configuration
config = get_config()

# Page configuration
st.set_page_config(
    page_title="Legal Document AI Simplifier",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .result-card {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .upload-area {
        border: 3px dashed #cbd5e0;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        background: #f8fafc;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI
@st.cache_resource
def get_llm():
    api_key = config.OPENAI_API_KEY
    if not api_key:
        st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
        return None
    
    return ChatOpenAI(
        model=config.OPENAI_MODEL,
        temperature=config.OPENAI_TEMPERATURE,
        api_key=api_key
    )



# Main application
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ Legal Document AI Simplifier</h1>
        <p style="font-size: 1.2rem; margin: 0;">Demystifying Legal Documents with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Settings")
        
        # API Key check
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            st.error("⚠️ OpenAI API key not found")
            st.info("Please set OPENAI_API_KEY in your environment variables or .env file")
        else:
            st.success("✅ OpenAI API key configured")
        
        st.markdown("---")
        
        # Model selection
        model = st.selectbox(
            "AI Model",
            ["gpt-4", "gpt-3.5-turbo"],
            index=0
        )
        
        temperature = st.slider(
            "Creativity Level",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Lower values = more focused, Higher values = more creative"
        )
        
        st.markdown("---")
        
        st.markdown("""
        ### 📚 How It Works
        
        1. **Upload Document**: PDF, DOCX, or TXT
        2. **AI Analysis**: Our AI processes the legal text
        3. **Simplified Output**: Get easy-to-understand explanations
        4. **Smart Insights**: Understand key terms and implications
        
        ### 🎯 Features
        
        - Multi-format document support
        - AI-powered text simplification
        - Legal term explanations
        - Document summarization
        - Interactive interface
        """)
    
    # Main content
    llm = get_llm()
    if not llm:
        st.stop()
    
    # Update model settings
    llm.model = model
    llm.temperature = temperature
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📄 Document Upload", "✍️ Text Input", "🔍 Term Explorer"])
    
    with tab1:
        st.header("📄 Upload Legal Document")
        
        uploaded_file = st.file_uploader(
            "Choose a legal document",
            type=config.ALLOWED_EXTENSIONS,
            help=f"Supported formats: {', '.join(config.ALLOWED_EXTENSIONS)} (Max 10MB)"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Extract text
            with st.spinner("📖 Extracting text from document..."):
                try:
                    extracted_text = extract_text_from_file(tmp_file_path, os.path.splitext(uploaded_file.name)[1])
                except ValueError as e:
                    st.error(str(e))
                    extracted_text = None
                finally:
                    os.remove(tmp_file_path)
            
            if extracted_text:
                st.subheader("📋 Extracted Text")
                st.text_area("Document Content", extracted_text, height=200, disabled=True)
                
                # Process with AI
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🧠 Simplify Text", use_container_width=True, key="simplify_doc"):
                        with st.spinner("🤖 AI is simplifying your legal text..."):
                            simplified = simplify_legal_text(extracted_text)
                            
                        st.subheader("💡 Simplified Text")
                        st.markdown(simplified)
                
                with col2:
                    if st.button("📝 Generate Summary", use_container_width=True, key="summarize_doc"):
                        with st.spinner("🤖 AI is generating a summary..."):
                            summary = generate_document_summary(extracted_text)
                            
                        st.subheader("📋 Document Summary")
                        st.markdown(summary)
    
    with tab2:
        st.header("✍️ Enter Text Directly")
        
        user_text = st.text_area(
            "Paste your legal text here",
            height=200,
            placeholder="Enter or paste legal text that you'd like to simplify..."
        )
        
        if user_text.strip():
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🧠 Simplify Text", use_container_width=True, key="simplify_text"):
                    with st.spinner("🤖 AI is simplifying your text..."):
                        simplified = simplify_legal_text(user_text)
                    
                    st.subheader("💡 Simplified Text")
                    st.markdown(simplified)
            
            with col2:
                if st.button("📝 Generate Summary", use_container_width=True, key="summarize_text"):
                    with st.spinner("🤖 AI is generating a summary..."):
                        summary = generate_document_summary(user_text)
                    
                    st.subheader("📋 Text Summary")
                    st.markdown(summary)
    
    with tab3:
        st.header("🔍 Legal Term Explorer")
        
        # Term input
        term = st.text_input(
            "Enter a legal term to explain",
            placeholder="e.g., 'force majeure', 'indemnification', 'breach of contract'"
        )
        
        if term:
            if st.button("🔍 Explain Term", use_container_width=True):
                with st.spinner("🤖 AI is explaining the term..."):
                    explanation = explain_legal_term(term)
                
                st.subheader(f"📚 Explanation: {term}")
                st.markdown(explanation)
        
        # Common legal terms
        st.subheader("📚 Common Legal Terms")
        
        common_terms = config.COMMON_LEGAL_TERMS
        
        cols = st.columns(3)
        for i, term_name in enumerate(common_terms):
            with cols[i % 3]:
                if st.button(term_name, use_container_width=True, key=f"term_{i}"):
                    with st.spinner(f"🤖 Explaining {term_name}..."):
                        explanation = explain_legal_term(term_name)
                    
                    st.subheader(f"📚 {term_name}")
                    st.markdown(explanation)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; padding: 2rem;">
        <p>⚖️ LegalDoc AI - Making legal documents accessible to everyone</p>
        <p style="font-size: 0.9rem;">Powered by OpenAI GPT models</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

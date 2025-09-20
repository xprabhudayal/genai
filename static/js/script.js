// Global variables
let currentResults = null;

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const textInput = document.getElementById('textInput');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeDragAndDrop();
    initializeFileInput();
    initializeTabs();
});

// Drag and Drop functionality
function initializeDragAndDrop() {
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
}

// File input functionality
function initializeFileInput() {
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

// Handle file upload
function handleFileUpload(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Please select a valid file type (PDF, DOCX, or TXT)', 'error');
        return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('File size must be less than 10MB', 'error');
        return;
    }

    // Show processing section
    showProcessing();
    
    // Create FormData and upload
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideProcessing();
        if (data.success) {
            currentResults = data;
            showResults(data);
        } else {
            showNotification(data.error || 'Error processing file', 'error');
        }
    })
    .catch(error => {
        hideProcessing();
        console.error('Error:', error);
        showNotification('Error uploading file. Please try again.', 'error');
    });
}

// Show processing section
function showProcessing() {
    processingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    uploadArea.style.opacity = '0.5';
    uploadArea.style.pointerEvents = 'none';
}

// Hide processing section
function hideProcessing() {
    processingSection.style.display = 'none';
    uploadArea.style.opacity = '1';
    uploadArea.style.pointerEvents = 'auto';
}

// Show results
function showResults(data) {
    // Update filename
    document.getElementById('filename').textContent = data.filename;
    
    // Update content
    document.getElementById('summaryContent').textContent = data.summary;
    document.getElementById('simplifiedContent').textContent = data.simplified_text;
    document.getElementById('originalContent').textContent = data.original_text;
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Tab functionality
function initializeTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and panes
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            this.classList.add('active');
            document.getElementById(targetTab + 'Tab').classList.add('active');
        });
    });
}

// Simplify text from textarea
function simplifyText() {
    const text = textInput.value.trim();
    if (!text) {
        showNotification('Please enter some text to simplify', 'warning');
        return;
    }

    showProcessing();
    
    fetch('/simplify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessing();
        if (data.success) {
            // Show simplified text in a modal or update the textarea
            showSimplifiedTextModal(data.simplified_text);
        } else {
            showNotification(data.error || 'Error simplifying text', 'error');
        }
    })
    .catch(error => {
        hideProcessing();
        console.error('Error:', error);
        showNotification('Error processing text. Please try again.', 'error');
    });
}

// Explain legal terms
function explainTerms() {
    const text = textInput.value.trim();
    if (!text) {
        showNotification('Please enter some text to analyze', 'warning');
        return;
    }

    // Extract potential legal terms (simple approach)
    const legalTerms = extractLegalTerms(text);
    
    if (legalTerms.length === 0) {
        showNotification('No legal terms found in the text', 'info');
        return;
    }

    // Show terms for user to select
    showTermsSelectionModal(legalTerms);
}

// Extract potential legal terms from text
function extractLegalTerms(text) {
    // Simple regex to find potential legal terms (capitalized words, common legal phrases)
    const legalPatterns = [
        /\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g, // Capitalized phrases
        /\b(?:hereby|whereas|hereinafter|aforesaid|pursuant|whereby|notwithstanding)\b/gi,
        /\b(?:party|parties|agreement|contract|terms|conditions|liability|damages|breach|termination)\b/gi
    ];
    
    const terms = new Set();
    
    legalPatterns.forEach(pattern => {
        const matches = text.match(pattern);
        if (matches) {
            matches.forEach(match => {
                if (match.length > 3) { // Filter out very short matches
                    terms.add(match.toLowerCase());
                }
            });
        }
    });
    
    return Array.from(terms).slice(0, 10); // Limit to 10 terms
}

// Show simplified text modal
function showSimplifiedTextModal(simplifiedText) {
    const modal = document.getElementById('termModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = 'Simplified Text';
    modalBody.innerHTML = `
        <div class="simplified-result">
            <h4>Your simplified text:</h4>
            <div class="text-content">${simplifiedText.replace(/\n/g, '<br>')}</div>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Show terms selection modal
function showTermsSelectionModal(terms) {
    const modal = document.getElementById('termModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = 'Select Terms to Explain';
    modalBody.innerHTML = `
        <div class="terms-selection">
            <p>Select legal terms to get explanations:</p>
            <div class="terms-grid">
                ${terms.map(term => `
                    <button class="term-btn" onclick="explainTerm('${term}')">
                        ${term.charAt(0).toUpperCase() + term.slice(1)}
                    </button>
                `).join('')}
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Explain a specific term
function explainTerm(term) {
    showProcessing();
    
    fetch('/explain', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ term: term })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessing();
        if (data.success) {
            showTermExplanationModal(term, data.explanation);
        } else {
            showNotification(data.error || 'Error explaining term', 'error');
        }
    })
    .catch(error => {
        hideProcessing();
        console.error('Error:', error);
        showNotification('Error explaining term. Please try again.', 'error');
    });
}

// Show term explanation modal
function showTermExplanationModal(term, explanation) {
    const modal = document.getElementById('termModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = `Explanation: ${term.charAt(0).toUpperCase() + term.slice(1)}`;
    modalBody.innerHTML = `
        <div class="term-explanation">
            <h4>${term.charAt(0).toUpperCase() + term.slice(1)}</h4>
            <div class="explanation-content">${explanation.replace(/\n/g, '<br>')}</div>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Close modal
function closeModal() {
    document.getElementById('termModal').style.display = 'none';
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('termModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#f56565' : type === 'warning' ? '#ed8936' : type === 'success' ? '#48bb78' : '#4299e1'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;
    
    // Add keyframe animation
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Add some additional CSS for notifications
const notificationStyles = `
    .notification-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        line-height: 1;
    }
    
    .notification-close:hover {
        opacity: 0.8;
    }
    
    .terms-selection {
        text-align: center;
    }
    
    .terms-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    .term-btn {
        background: #667eea;
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    
    .term-btn:hover {
        background: #5a67d8;
        transform: translateY(-2px);
    }
    
    .simplified-result,
    .term-explanation {
        line-height: 1.6;
    }
    
    .text-content,
    .explanation-content {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-top: 1rem;
        white-space: pre-line;
    }
`;

// Add notification styles to the page
if (!document.querySelector('#notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = notificationStyles;
    document.head.appendChild(style);
}

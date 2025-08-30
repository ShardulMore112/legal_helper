// Global variables
let currentSessionId = null;
let websocket = null;
let isProcessing = false;

// DOM elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const actionSection = document.getElementById('actionSection');
const resultsSection = document.getElementById('resultsSection');
const chatSection = document.getElementById('chatSection');
const loadingSpinner = document.getElementById('loadingSpinner');
const browseLink = document.querySelector('.browse-link');

// Buttons
const explainBtn = document.getElementById('explainBtn');
const ragBtn = document.getElementById('ragBtn');
const newDocBtn = document.getElementById('newDocBtn');
const sendBtn = document.getElementById('sendBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const closeChatBtn = document.getElementById('closeChatBtn');

// Chat elements
const chatInput = document.getElementById('chatInput');
const chatMessages = document.getElementById('chatMessages');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    // Drag and drop events
    dropzone.addEventListener('dragover', handleDragOver);
    dropzone.addEventListener('dragleave', handleDragLeave);
    dropzone.addEventListener('drop', handleDrop);
    dropzone.addEventListener('click', () => fileInput.click());
    browseLink.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Button events
    explainBtn.addEventListener('click', handleExplain);
    ragBtn.addEventListener('click', handleRAG);
    newDocBtn.addEventListener('click', resetApp);
    sendBtn.addEventListener('click', sendMessage);
    clearChatBtn.addEventListener('click', clearChat);
    closeChatBtn.addEventListener('click', closeChat);

    // Chat input events
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Prevent default drag behaviors on document
    document.addEventListener('dragover', (e) => e.preventDefault());
    document.addEventListener('drop', (e) => e.preventDefault());
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    dropzone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropzone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    dropzone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
}

// File upload handler
async function handleFileUpload(file) {
    if (isProcessing) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'text/plain', 'image/jpeg', 'image/jpg'];
    const allowedExtensions = ['.pdf', '.txt', '.jpg', '.jpeg'];

    const fileName = file.name.toLowerCase();
    const fileExtension = fileName.substring(fileName.lastIndexOf('.'));

    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showUploadStatus('Please upload PDF, TXT, JPG, or JPEG files only.', 'error');
        return;
    }

    // Validate file size (max 50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showUploadStatus('File size must be less than 50MB.', 'error');
        return;
    }

    isProcessing = true;
    showLoading(true);
    dropzone.classList.add('upload-animation');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            currentSessionId = result.session_id;
            showUploadStatus(`File "${result.filename}" uploaded successfully! (${formatFileSize(result.file_size)})`, 'success');
            showActionSection();
        } else {
            showUploadStatus(result.detail || 'Upload failed', 'error');
        }
    } catch (error) {
        showUploadStatus('Network error. Please try again.', 'error');
        console.error('Upload error:', error);
    } finally {
        isProcessing = false;
        showLoading(false);
        dropzone.classList.remove('upload-animation');
        setTimeout(() => {
            fileInput.value = '';
        }, 100);
    }
}

// Show upload status
function showUploadStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `upload-status ${type}`;
    uploadStatus.style.display = 'block';

    // Auto-hide success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            uploadStatus.style.display = 'none';
        }, 3000);
    }
}

// Show action section
function showActionSection() {
    actionSection.style.display = 'block';
    actionSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Handle document explanation
async function handleExplain() {
    if (!currentSessionId || isProcessing) return;

    isProcessing = true;
    showLoading(true);

    try {
        const response = await fetch(`/explain/${currentSessionId}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (response.ok) {
            showResults('Document Explanation', formatExplanation(result));
        } else {
            showUploadStatus(result.detail || 'Failed to explain document', 'error');
        }
    } catch (error) {
        showUploadStatus('Network error. Please try again.', 'error');
        console.error('Explanation error:', error);
    } finally {
        isProcessing = false;
        showLoading(false);
    }
}

// Handle RAG chatbot creation
async function handleRAG() {
    if (!currentSessionId || isProcessing) return;

    isProcessing = true;
    showLoading(true);

    try {
        const response = await fetch(`/create-rag/${currentSessionId}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (response.ok) {
            initializeChat();
        } else {
            showUploadStatus(result.detail || 'Failed to create RAG session', 'error');
        }
    } catch (error) {
        showUploadStatus('Network error. Please try again.', 'error');
        console.error('RAG creation error:', error);
    } finally {
        isProcessing = false;
        showLoading(false);
    }
}

// Initialize chat with WebSocket
function initializeChat() {
    hideAllSections();
    chatSection.style.display = 'block';
    chatSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${currentSessionId}`;

    websocket = new WebSocket(wsUrl);

    websocket.onopen = function(event) {
        console.log('WebSocket connection opened');
        addMessage('Connected to RAG chatbot successfully!', 'system');
    };

    websocket.onmessage = function(event) {
        addMessage(event.data, 'bot');
    };

    websocket.onclose = function(event) {
        console.log('WebSocket connection closed');
        addMessage('Connection closed. Please refresh to reconnect.', 'system');
    };

    websocket.onerror = function(error) {
        console.error('WebSocket error:', error);
        addMessage('Connection error. Please try again.', 'system');
    };
}

// Send chat message
function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !websocket || websocket.readyState !== WebSocket.OPEN) return;

    addMessage(message, 'user');
    websocket.send(message);
    chatInput.value = '';

    // Disable send button temporarily
    sendBtn.disabled = true;
    setTimeout(() => {
        sendBtn.disabled = false;
    }, 1000);
}

// Add message to chat
function addMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    if (type === 'bot' && message.startsWith('Bot: ')) {
        messageDiv.textContent = message.substring(5);
    } else {
        messageDiv.textContent = message;
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Clear chat messages
function clearChat() {
    chatMessages.innerHTML = '';
    addMessage('Chat cleared. You can continue asking questions.', 'system');
}

// Close chat and return to results
function closeChat() {
    if (websocket) {
        websocket.close();
        websocket = null;
    }
    chatSection.style.display = 'none';
    actionSection.style.display = 'block';
    actionSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Show results section
function showResults(title, content) {
    hideAllSections();

    document.getElementById('resultsTitle').textContent = title;
    document.getElementById('resultsContent').innerHTML = content;

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Format explanation content
function formatExplanation(data) {
    let html = `
        <div class="explanation-header">
            <h4><i class="fas fa-file"></i> ${data.filename}</h4>
            <p><strong>Document Type:</strong> ${data.document_type}</p>
        </div>
        <div class="explanation-content">
            ${data.explanation.replace(/\n/g, '<br><br>')}
        </div>
    `;
    return html;
}

// Hide all main sections
function hideAllSections() {
    actionSection.style.display = 'none';
    resultsSection.style.display = 'none';
    chatSection.style.display = 'none';
}

// Reset application to initial state
function resetApp() {
    // Close WebSocket if open
    if (websocket) {
        websocket.close();
        websocket = null;
    }

    // Delete current session
    if (currentSessionId) {
        fetch(`/session/${currentSessionId}`, { method: 'DELETE' })
            .catch(error => console.error('Error deleting session:', error));
    }

    // Reset variables
    currentSessionId = null;
    isProcessing = false;

    // Reset UI
    hideAllSections();
    uploadStatus.style.display = 'none';
    fileInput.value = '';
    chatInput.value = '';
    chatMessages.innerHTML = '';

    // Smooth scroll to top
    document.querySelector('.header').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// Show/hide loading spinner
function showLoading(show) {
    loadingSpinner.style.display = show ? 'flex' : 'none';
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Add scroll to top functionality
function addScrollToTop() {
    const scrollBtn = document.createElement('button');
    scrollBtn.className = 'scroll-top';
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.style.display = 'none';
    document.body.appendChild(scrollBtn);

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });

    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// Initialize scroll to top when DOM is loaded
document.addEventListener('DOMContentLoaded', addScrollToTop);

// Handle page beforeunload to cleanup
window.addEventListener('beforeunload', () => {
    if (websocket) {
        websocket.close();
    }
});

// Error handling for uncaught errors
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showUploadStatus('An unexpected error occurred. Please refresh the page.', 'error');
});

// Handle network status changes
window.addEventListener('online', () => {
    showUploadStatus('Connection restored.', 'success');
});

window.addEventListener('offline', () => {
    showUploadStatus('No internet connection. Please check your network.', 'error');
});

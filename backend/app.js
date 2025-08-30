// Legal Document AI Assistant JavaScript

class LegalDocumentAssistant {
    constructor() {
        this.currentFile = null;
        this.sessionId = null;
        this.chatHistory = [];
        this.sampleExplanations = {
            "Non-Disclosure Agreement": "This Non-Disclosure Agreement (NDA) is a legal contract that creates a confidential relationship between two or more parties. **Purpose and Overview:** The primary purpose of this document is to protect sensitive information from being shared with unauthorized parties. Think of it as a legal 'promise to keep secrets' that has serious consequences if broken.\n\n**Key Parties Involved:** This agreement typically involves a 'Disclosing Party' (the person or company sharing confidential information) and a 'Receiving Party' (the person or company that will have access to this information). Both parties have specific legal obligations under this agreement.\n\n**What Information is Protected:** The NDA covers various types of confidential information including business strategies, customer lists, financial data, technical specifications, trade secrets, and any other proprietary information. This protection extends to verbal, written, and electronic communications.\n\n**Legal Obligations and Restrictions:** The receiving party must keep all information strictly confidential, use it only for the specified purpose, and cannot share it with anyone else without written permission. They also cannot use this information to compete against the disclosing party or for their own benefit beyond the agreed scope.\n\n**Duration and Scope:** NDAs specify how long the confidentiality obligations last (often 2-5 years or indefinitely for trade secrets) and clearly define what constitutes confidential information versus public knowledge.\n\n**Consequences of Breach:** If someone violates the NDA, they may face serious legal consequences including monetary damages, injunctive relief (court orders to stop the violation), and payment of legal fees. The agreement may also specify liquidated damages - predetermined amounts to be paid for breaches.",
            "Court Order": "This Court Order is an official directive issued by a judge or magistrate that legally requires specific actions to be taken or prohibits certain behaviors. **Nature and Authority:** A court order carries the full force of law and must be obeyed by all parties mentioned in the document. Failure to comply can result in contempt of court charges, fines, or even imprisonment.\n\n**Parties and Jurisdiction:** The order identifies the specific court issuing the directive, the presiding judge, and all parties who must comply with the order. It also establishes the legal jurisdiction and authority under which the order is issued.\n\n**Specific Directives:** Court orders contain precise instructions about what must be done, when it must be completed, and by whom. This might include paying money, transferring property, stopping certain activities, or appearing in court on specific dates.\n\n**Legal Basis:** The order explains the legal reasoning behind the directive, often referencing specific laws, previous court decisions, or evidence presented in the case. This provides the foundation for the court's authority to issue such an order.\n\n**Compliance Requirements:** The document outlines exactly what each party must do to comply, including specific deadlines, reporting requirements, and consequences for non-compliance. \n\n**Enforcement Mechanisms:** If someone fails to follow the court order, the document typically explains the enforcement procedures, which may include additional penalties, asset seizure, or criminal charges for contempt of court.",
            "Service Agreement": "This Service Agreement is a legally binding contract that outlines the terms and conditions for services to be provided between two parties. **Purpose and Scope:** This document establishes a professional relationship where one party (the service provider) agrees to perform specific services for another party (the client) in exchange for compensation.\n\n**Service Description:** The agreement provides detailed descriptions of what services will be performed, including specific deliverables, quality standards, timelines, and performance metrics. This section acts like a detailed job description that both parties must follow.\n\n**Payment Terms and Structure:** The document clearly outlines how much will be paid, when payments are due, what payment methods are accepted, and any penalties for late payment. This might include hourly rates, fixed fees, milestone payments, or recurring charges.\n\n**Responsibilities and Obligations:** Both parties have specific responsibilities clearly defined in the agreement. The service provider must deliver services according to agreed standards, while the client must provide necessary cooperation, materials, or access required for service delivery.\n\n**Timeline and Milestones:** The agreement establishes start dates, completion deadlines, and any intermediate milestones. This creates accountability and helps both parties plan their resources and expectations.\n\n**Legal Protections:** The document includes provisions for handling disputes, intellectual property rights, confidentiality requirements, liability limitations, and termination procedures. These protect both parties if something goes wrong or if the relationship needs to end early."
        };

        this.chatSamples = [
            {
                question: "What are the main parties in this agreement?",
                answer: "Based on the document, the main parties are the Service Provider and the Client. The Service Provider is responsible for delivering the specified services according to the agreed standards, while the Client must provide necessary cooperation, materials, and timely payments as outlined in the agreement."
            },
            {
                question: "What are the key deadlines I need to know about?",
                answer: "The document contains several important deadlines: Initial service delivery within 30 days of agreement execution, milestone reviews every 2 weeks, final deliverables due 90 days from start date, and payment terms of Net 15 days. Missing these deadlines could result in contract penalties or termination rights for the non-breaching party."
            },
            {
                question: "What happens if someone breaches this contract?",
                answer: "If there's a breach of this contract, several consequences may apply: The non-breaching party may terminate the agreement with written notice, seek monetary damages for losses incurred, request specific performance of obligations, and recover attorney fees and court costs. The document also requires mediation before pursuing litigation."
            },
            {
                question: "Are there any confidentiality requirements?",
                answer: "Yes, the document includes comprehensive confidentiality provisions. Both parties must protect proprietary information, trade secrets, and sensitive business data. These obligations survive contract termination and typically last for 2-3 years. Violations may result in injunctive relief and monetary damages."
            },
            {
                question: "What are the payment terms?",
                answer: "The payment structure includes an initial deposit of 25% upon signing, milestone payments of 50% at mid-project completion, and final payment of 25% upon delivery. All invoices are due within 15 days, with late fees of 1.5% per month on overdue amounts. Payments can be made via check, wire transfer, or ACH."
            },
            {
                question: "Can this contract be terminated early?",
                answer: "Yes, the contract allows for early termination under specific circumstances: Either party may terminate with 30 days written notice, immediate termination is allowed for material breach that isn't cured within 15 days, and termination for convenience requires payment for work completed plus reasonable wind-down costs."
            }
        ];

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupEventListeners());
        } else {
            this.setupEventListeners();
        }
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Get all required elements
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');

        if (!uploadZone || !fileInput || !browseBtn) {
            console.error('Required elements not found:', {
                uploadZone: !!uploadZone,
                fileInput: !!fileInput,
                browseBtn: !!browseBtn
            });
            return;
        }

        console.log('All required elements found, setting up listeners...');

        // Drag and drop events for upload zone
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.processFile(files[0]);
            }
        });

        // Click event for upload zone (but not for the browse button)
        uploadZone.addEventListener('click', (e) => {
            // Only trigger if not clicking the browse button
            if (e.target !== browseBtn && !browseBtn.contains(e.target)) {
                e.preventDefault();
                e.stopPropagation();
                fileInput.click();
            }
        });

        // Browse button click event
        browseBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Browse button clicked');
            fileInput.click();
        });

        // File input change event
        fileInput.addEventListener('change', (e) => {
            console.log('File input changed:', e.target.files);
            const file = e.target.files[0];
            if (file) {
                this.processFile(file);
            }
        });

        // Action buttons
        const explainBtn = document.getElementById('explainBtn');
        const chatBtn = document.getElementById('chatBtn');
        
        if (explainBtn) {
            explainBtn.addEventListener('click', () => {
                console.log('Explain button clicked');
                this.handleExplainDocument();
            });
        }
        
        if (chatBtn) {
            chatBtn.addEventListener('click', () => {
                console.log('Chat button clicked');
                this.handleStartChat();
            });
        }

        // Chat functionality
        const sendBtn = document.getElementById('sendBtn');
        const chatInput = document.getElementById('chatInput');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.handleSendMessage());
        }
        
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });
        }

        // Control buttons
        const newSessionBtn = document.getElementById('newSessionBtn');
        const newChatSessionBtn = document.getElementById('newChatSessionBtn');
        const clearChatBtn = document.getElementById('clearChatBtn');
        
        if (newSessionBtn) {
            newSessionBtn.addEventListener('click', () => this.startNewSession());
        }
        
        if (newChatSessionBtn) {
            newChatSessionBtn.addEventListener('click', () => this.startNewSession());
        }
        
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => this.clearChat());
        }

        console.log('Event listeners setup complete');
    }

    processFile(file) {
        console.log('Processing file:', file.name, file.type, file.size);
        
        // Validate file type
        const allowedTypes = ['.pdf', '.txt', '.jpg', '.jpeg'];
        const fileName = file.name.toLowerCase();
        const hasValidExtension = allowedTypes.some(ext => fileName.endsWith(ext));
        
        if (!hasValidExtension) {
            alert('Please upload a valid file type: PDF, TXT, JPG, or JPEG');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10MB');
            return;
        }

        this.currentFile = file;
        this.sessionId = this.generateSessionId();
        
        console.log('File validated, showing loading...');
        
        // Show loading
        this.showLoading();

        // Simulate file processing
        setTimeout(() => {
            this.hideLoading();
            this.showUploadSuccess();
        }, 2000);
    }

    generateSessionId() {
        return 'DOC-' + Math.random().toString(36).substr(2, 9).toUpperCase();
    }

    showLoading() {
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('hidden');
            console.log('Loading overlay shown');
        }
    }

    hideLoading() {
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('hidden');
            console.log('Loading overlay hidden');
        }
    }

    showUploadSuccess() {
        console.log('Showing upload success');
        
        // Update status
        const statusText = document.getElementById('statusText');
        const sessionIdEl = document.getElementById('sessionId');
        
        if (statusText) statusText.textContent = `${this.currentFile.name} uploaded successfully!`;
        if (sessionIdEl) sessionIdEl.textContent = this.sessionId;
        
        // Show sections
        const uploadStatus = document.getElementById('uploadStatus');
        const actionSection = document.getElementById('actionSection');
        
        if (uploadStatus) uploadStatus.classList.remove('hidden');
        if (actionSection) actionSection.classList.remove('hidden');
        
        // Hide other sections
        const resultsSection = document.getElementById('resultsSection');
        const chatSection = document.getElementById('chatSection');
        
        if (resultsSection) resultsSection.classList.add('hidden');
        if (chatSection) chatSection.classList.add('hidden');
    }

    handleExplainDocument() {
        console.log('Handling explain document');
        this.showLoading();
        
        setTimeout(() => {
            this.hideLoading();
            this.showDocumentExplanation();
        }, 1500);
    }

    showDocumentExplanation() {
        console.log('Showing document explanation');
        
        // Get a random explanation
        const explanationKeys = Object.keys(this.sampleExplanations);
        const randomKey = explanationKeys[Math.floor(Math.random() * explanationKeys.length)];
        const explanation = this.sampleExplanations[randomKey];
        
        // Format explanation with markdown-like styling
        const formattedExplanation = this.formatExplanation(explanation);
        
        const explanationText = document.getElementById('explanationText');
        if (explanationText) explanationText.innerHTML = formattedExplanation;
        
        const resultsSection = document.getElementById('resultsSection');
        const chatSection = document.getElementById('chatSection');
        
        if (resultsSection) resultsSection.classList.remove('hidden');
        if (chatSection) chatSection.classList.add('hidden');
        
        // Scroll to results
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    formatExplanation(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<h3>$1</h3>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }

    handleStartChat() {
        console.log('Starting chat');
        
        this.chatHistory = [];
        const resultsSection = document.getElementById('resultsSection');
        const chatSection = document.getElementById('chatSection');
        
        if (resultsSection) resultsSection.classList.add('hidden');
        if (chatSection) chatSection.classList.remove('hidden');
        
        // Reset chat messages to just the initial message
        this.resetChatMessages();
        
        // Scroll to chat
        if (chatSection) {
            chatSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    resetChatMessages() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = `
                <div class="message assistant-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <p>Hello! I've analyzed your document "${this.currentFile ? this.currentFile.name : 'your document'}". Feel free to ask me any questions about its contents, key terms, obligations, or legal implications.</p>
                    </div>
                </div>
            `;
        }
    }

    handleSendMessage() {
        const chatInput = document.getElementById('chatInput');
        if (!chatInput) return;
        
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        console.log('Sending message:', message);
        
        // Add user message
        this.addMessage(message, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Generate response after delay
        setTimeout(() => {
            this.hideTypingIndicator();
            const response = this.generateResponse(message);
            this.addMessage(response, 'assistant');
        }, 1000 + Math.random() * 2000);
    }

    addMessage(text, sender) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <p>${text}</p>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store in history
        this.chatHistory.push({ text, sender });
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>Analyzing your question...</p>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    generateResponse(question) {
        const lowerQuestion = question.toLowerCase();
        
        // Check for specific keywords and provide relevant responses
        if (lowerQuestion.includes('parties') || lowerQuestion.includes('who')) {
            return this.chatSamples[0].answer;
        } else if (lowerQuestion.includes('deadline') || lowerQuestion.includes('date') || lowerQuestion.includes('when')) {
            return this.chatSamples[1].answer;
        } else if (lowerQuestion.includes('breach') || lowerQuestion.includes('violation') || lowerQuestion.includes('break')) {
            return this.chatSamples[2].answer;
        } else if (lowerQuestion.includes('confidential') || lowerQuestion.includes('secret') || lowerQuestion.includes('private')) {
            return this.chatSamples[3].answer;
        } else if (lowerQuestion.includes('payment') || lowerQuestion.includes('money') || lowerQuestion.includes('pay')) {
            return this.chatSamples[4].answer;
        } else if (lowerQuestion.includes('terminate') || lowerQuestion.includes('end') || lowerQuestion.includes('cancel')) {
            return this.chatSamples[5].answer;
        } else {
            // Default responses for general questions
            const generalResponses = [
                "Based on the document analysis, this appears to be a standard legal agreement with specific terms and conditions. Could you be more specific about what aspect you'd like me to explain?",
                "I can help clarify any specific clauses or terms in your document. What particular section or concept would you like me to break down for you?",
                "This document contains several important legal provisions. Would you like me to explain the obligations, rights, or potential risks involved?",
                "I've identified key sections in your document including definitions, obligations, and remedies. What specific area interests you most?",
                "The document includes standard legal language that I can help translate into plain English. What specific terms or sections are you curious about?"
            ];
            return generalResponses[Math.floor(Math.random() * generalResponses.length)];
        }
    }

    clearChat() {
        this.chatHistory = [];
        this.resetChatMessages();
    }

    startNewSession() {
        console.log('Starting new session');
        
        // Reset all state
        this.currentFile = null;
        this.sessionId = null;
        this.chatHistory = [];
        
        // Reset UI
        const uploadStatus = document.getElementById('uploadStatus');
        const actionSection = document.getElementById('actionSection');
        const resultsSection = document.getElementById('resultsSection');
        const chatSection = document.getElementById('chatSection');
        
        if (uploadStatus) uploadStatus.classList.add('hidden');
        if (actionSection) actionSection.classList.add('hidden');
        if (resultsSection) resultsSection.classList.add('hidden');
        if (chatSection) chatSection.classList.add('hidden');
        
        // Reset file input
        const fileInput = document.getElementById('fileInput');
        if (fileInput) fileInput.value = '';
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Legal Document Assistant');
    new LegalDocumentAssistant();
});
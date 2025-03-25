document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const clearChatButton = document.getElementById('clear-chat');
    const typingIndicator = document.getElementById('typing-indicator');
    
    // Allow multiple file selection
    fileInput.setAttribute('multiple', 'multiple');
    
    // Auto-resize the message input as the user types
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        const newHeight = Math.min(this.scrollHeight, 150);
        this.style.height = `${newHeight}px`;
        validateSendButton();
    });
    
    // Handle file input change
    fileInput.addEventListener('change', function() {
        const files = Array.from(this.files);
        const fileNames = files.map(file => file.name).join(', ');
        
        // Check file sizes (max 20MB each)
        const oversizedFiles = files.filter(file => file.size > 50 * 1024 * 1024);
        if (oversizedFiles.length > 0) {
            alert('One or more files are too large. Maximum file size is 50 MB.');
            this.value = '';
            fileName.textContent = '';
            return;
        }
        
        // Display file names
        fileName.textContent = fileNames;
        validateSendButton();
    });
    
    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const messageText = messageInput.value.trim();
        const files = Array.from(fileInput.files);
        
        if (!messageText && files.length === 0) return;
        
        const formData = new FormData();
        if (messageText) formData.append('message', messageText);
        files.forEach(file => formData.append('files', file));
        
        if (messageText) {
            addMessageToUI('user', messageText);
        } else if (files.length > 0) {
            addMessageToUI('user', `Uploading files: ${files.map(file => file.name).join(', ')}...`);
        }
        
        messageInput.value = '';
        messageInput.style.height = '40px';
        fileInput.value = '';
        fileName.textContent = '';
        sendButton.disabled = true;
        showTypingIndicator();
        scrollToBottom();
        
        fetch('/send_message', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideTypingIndicator();
            addMessageToUI('agent', data.agent_response.text);
            scrollToBottom();
        })
        .catch(error => {
            hideTypingIndicator();
            addErrorMessage('Sorry, there was a problem sending your message. Please try again.');
            console.error('Error:', error);
            scrollToBottom();
        });
    });
    
    clearChatButton.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            fetch('/clear_chat', {
                method: 'POST',
            })
            .then(response => {
                if (response.ok) {
                    chatMessages.innerHTML = `
                        <div class="empty-chat">
                            <div class="welcome-message">
                                <i class="fas fa-robot welcome-icon"></i>
                                <h2>Welcome to AI Agent Chat</h2>
                                <p>Start a conversation or upload a file to get assistance from an agent.</p>
                            </div>
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error clearing chat:', error);
            });
        }
    });
    
    function validateSendButton() {
        sendButton.disabled = messageInput.value.trim() === '' && fileInput.files.length === 0;
    }
    
    function addMessageToUI(sender, text, fileUrl = null) {
        const emptyChat = chatMessages.querySelector('.empty-chat');
        if (emptyChat) {
            chatMessages.removeChild(emptyChat);
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const now = new Date();
        const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">${sender === 'user' ? 'You' : 'AI Assistant'}</span>
                    <span class="timestamp">${time}</span>
                </div>
                <div class="message-text ${sender === 'agent' ? 'markdown-body' : ''}">${sender === 'user' ? formatMessageText(text) : text}</div>
                ${fileUrl ? `
                <div class="file-attachment">
                    <i class="fas fa-file-alt"></i>
                    <a href="${fileUrl}" target="_blank">View uploaded file</a>
                </div>
                ` : ''}
            </div>
        `;
        
        messageDiv.style.opacity = '0';
        chatMessages.appendChild(messageDiv);
        void messageDiv.offsetWidth;
        messageDiv.style.opacity = '1';
    }
    
    function formatMessageText(text) {
        let formatted = text.replace(/\n/g, '<br>');
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        formatted = formatted.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
        return formatted;
    }
    
    function addErrorMessage(text) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = text;
        chatMessages.appendChild(errorDiv);
        
        setTimeout(() => {
            if (errorDiv.parentNode === chatMessages) {
                chatMessages.removeChild(errorDiv);
            }
        }, 5000);
    }
    
    function showTypingIndicator() {
        typingIndicator.classList.remove('hidden');
    }
    
    function hideTypingIndicator() {
        typingIndicator.classList.add('hidden');
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    messageInput.dispatchEvent(new Event('input'));
    scrollToBottom();
});

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const emptyState = document.getElementById('empty-state');
    const newChatBtn = document.getElementById('new-chat-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    // Configure marked.js for safe markdown rendering
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (role === 'bot') {
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.id = 'typing-indicator';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const query = userInput.value.trim();
        if (!query) return;

        // Hide empty state on first message
        if (emptyState && emptyState.style.display !== 'none') {
            emptyState.style.display = 'none';
        }

        // 1. Show user message
        appendMessage('user', query);
        userInput.value = '';
        
        // 2. Show typing indicator
        showTypingIndicator();

        try {
            // 3. Call API
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();
            
            // 4. Remove typing indicator and show response
            removeTypingIndicator();
            
            if (response.ok) {
                appendMessage('bot', data.answer);
            } else {
                appendMessage('bot', "Xin lỗi, đã có lỗi xảy ra: " + (data.detail || "Lỗi máy chủ"));
            }
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            appendMessage('bot', "Xin lỗi, không thể kết nối tới máy chủ. Vui lòng thử lại sau.");
        }
    });

    // New Chat Button functionality
    newChatBtn.addEventListener('click', () => {
        // Clear all messages except empty state
        const messages = chatMessages.querySelectorAll('.message');
        messages.forEach(msg => msg.remove());
        
        // Show empty state again
        if (emptyState) {
            emptyState.style.display = 'flex';
        }
    });

    // Clear History Button functionality
    clearHistoryBtn.addEventListener('click', () => {
        // Clear all messages except empty state
        const messages = chatMessages.querySelectorAll('.message');
        messages.forEach(msg => msg.remove());
        
        // Show empty state again
        if (emptyState) {
            emptyState.style.display = 'flex';
        }
        
        // If there was a backend endpoint to clear history, call it here
        // fetch('/clear-history', { method: 'POST' });
    });
});

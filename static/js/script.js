document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const userInfoForm = document.getElementById('userInfoForm');
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const chatContainer = document.getElementById('chatContainer');
    const nutritionSummary = document.getElementById('nutritionSummary');
    
    // Store nutrition data
    let nutritionData = null;
    
    // Store chat history
    let chatHistory = [];
    
    // Form validation and submission
    userInfoForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!userInfoForm.checkValidity()) {
            e.stopPropagation();
            userInfoForm.classList.add('was-validated');
            return;
        }
        
        // Collect form data
        const formData = {
            height: parseFloat(document.getElementById('height').value),
            weight: parseFloat(document.getElementById('weight').value),
            age: parseInt(document.getElementById('age').value),
            gender: document.querySelector('input[name="gender"]:checked').value,
            activityLevel: document.getElementById('activityLevel').value,
            goal: document.getElementById('goal').value,
            dietType: document.getElementById('dietType').value,
            metabolicType: document.querySelector('input[name="metabolicType"]:checked').value
        };
        
        // Calculate nutrition
        calculateNutrition(formData);
    });
    
    // Message form handling
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessageToChat(message, false);
        
        // Clear input
        messageInput.value = '';
        
        // Send message to backend
        sendMessage(message);
    });
    
    // Calculate nutrition function
    function calculateNutrition(userData) {
        // Show loading message
        addMessageToChat('Calculating your personalized nutrition plan...', true);
        
        // Disable form during calculation
        toggleFormInputs(userInfoForm, true);
        
        // Send data to backend
        fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Store nutrition data
            nutritionData = data;
            
            // Update nutrition summary
            updateNutritionSummary(data);
            
            // Enable chat
            messageInput.disabled = false;
            sendButton.disabled = false;
            
            // Show success message
            const message = `I've calculated your personalized nutrition plan! You need approximately ${data.daily_calories} calories per day with ${data.macros.protein}g protein, ${data.macros.carbs}g carbs, and ${data.macros.fat}g fat.
            
            What would you like to know about your nutrition plan? You can ask me about:
            - Meal ideas that fit your macros
            - Tips for your ${userData.goal} goal
            - Foods high in protein/carbs/fat
            - Strategies for your ${userData.dietType} diet
            - How to adjust your plan based on your ${userData.metabolicType} metabolic type`;
            
            addMessageToChat(message, true);
            
            // Re-enable form
            toggleFormInputs(userInfoForm, false);
        })
        .catch(error => {
            console.error('Error calculating nutrition:', error);
            addMessageToChat('Sorry, there was an error calculating your nutrition plan. Please try again.', true);
            
            // Re-enable form
            toggleFormInputs(userInfoForm, false);
        });
    }
    
    // Send message to backend
    function sendMessage(message) {
        // Disable input during processing
        messageInput.disabled = true;
        sendButton.disabled = true;
        
        // Add loading indicator
        const loadingId = 'loading-' + Date.now();
        chatContainer.innerHTML += `
            <div class="message bot-message" id="${loadingId}">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        scrollToBottom();
        
        // Send data to backend
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                nutritionData: nutritionData,
                chatHistory: chatHistory
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove loading indicator
            document.getElementById(loadingId).remove();
            
            // Add response to chat
            addMessageToChat(data.response, true);
            
            // Re-enable input
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        })
        .catch(error => {
            console.error('Error sending message:', error);
            
            // Remove loading indicator
            document.getElementById(loadingId).remove();
            
            // Add error message
            addMessageToChat('Sorry, there was an error processing your message. Please try again.', true);
            
            // Re-enable input
            messageInput.disabled = false;
            sendButton.disabled = false;
        });
    }
    
    // Add message to chat
    function addMessageToChat(message, isBot) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${isBot ? 'bot-message' : 'user-message'}`;
        
        const avatarEl = document.createElement('div');
        avatarEl.className = 'message-avatar';
        avatarEl.innerHTML = isBot ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        
        // Format message with line breaks and whitespace
        const formattedMessage = message.replace(/\n/g, '<br>');
        contentEl.innerHTML = formattedMessage;
        
        messageEl.appendChild(avatarEl);
        messageEl.appendChild(contentEl);
        
        chatContainer.appendChild(messageEl);
        
        // Scroll to bottom
        scrollToBottom();
        
        // Add to chat history
        chatHistory.push({
            message: message,
            isBot: isBot
        });
    }
    
    // Update nutrition summary
    function updateNutritionSummary(data) {
        // Update summary values
        document.getElementById('summaryCalories').textContent = data.daily_calories;
        document.getElementById('summaryProtein').textContent = data.macros.protein + 'g';
        document.getElementById('summaryCarbs').textContent = data.macros.carbs + 'g';
        document.getElementById('summaryFat').textContent = data.macros.fat + 'g';
        
        // Show summary section
        nutritionSummary.style.display = 'block';
    }
    
    // Toggle form inputs
    function toggleFormInputs(form, disabled) {
        const inputs = form.querySelectorAll('input, select, button');
        inputs.forEach(input => {
            input.disabled = disabled;
        });
    }
    
    // Scroll chat to bottom
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});

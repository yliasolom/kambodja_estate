пше// Main script for explainer page interactivity

let currentQuestion = null;
let hasShownAnswer = false;
let currentSlideIndex = 0;

// Configuration
const API_URL = '/api/ask';  // Same domain
const API_STREAM_URL = '/api/ask/stream';  // Same domain
const PROPERTY_URL = 'https://www.realestate.com.kh/boreys/borey-peng-huoth-the-star-platinum-mastery/5-bed-6-bath-villa-258405/';
const USE_STREAMING = true;  // Enable streaming

// Question type to text mapping
const QUESTION_TEXTS = {
    'can_i_own': 'Can I own this villa as a foreigner?',
    'lease_works': 'How does the land lease work?',
    'is_safe': 'Is this legal and safe?',
    'costs': 'What are the costs involved?'
};

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Add click handlers to question buttons
    const questionButtons = document.querySelectorAll('.question-btn');
    questionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const questionType = this.getAttribute('data-question');
            askQuestion(questionType);
        });
    });
    
    // Add Enter key handler for custom question input
    const customInput = document.getElementById('customQuestionInput');
    if (customInput) {
        customInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askCustomQuestion();
            }
        });
    }
    
    // Initialize carousel
    initCarousel();
});

// Carousel Functions
function initCarousel() {
    const slides = document.querySelectorAll('.carousel-slide');
    const totalSlides = slides.length;
    
    if (totalSlides > 0) {
        document.getElementById('totalSlides').textContent = totalSlides;
        updateSlideCounter();
    }
}

function changeSlide(direction) {
    const slides = document.querySelectorAll('.carousel-slide');
    const thumbs = document.querySelectorAll('.carousel-thumb');
    const totalSlides = slides.length;
    
    // Remove active class from current slide
    slides[currentSlideIndex].classList.remove('active');
    thumbs[currentSlideIndex].classList.remove('active');
    
    // Calculate new index
    currentSlideIndex = (currentSlideIndex + direction + totalSlides) % totalSlides;
    
    // Add active class to new slide
    slides[currentSlideIndex].classList.add('active');
    thumbs[currentSlideIndex].classList.add('active');
    
    updateSlideCounter();
}

function goToSlide(index) {
    const slides = document.querySelectorAll('.carousel-slide');
    const thumbs = document.querySelectorAll('.carousel-thumb');
    
    // Remove active class from current
    slides[currentSlideIndex].classList.remove('active');
    thumbs[currentSlideIndex].classList.remove('active');
    
    // Set new index
    currentSlideIndex = index;
    
    // Add active class to new
    slides[currentSlideIndex].classList.add('active');
    thumbs[currentSlideIndex].classList.add('active');
    
    updateSlideCounter();
}

function updateSlideCounter() {
    document.getElementById('currentSlide').textContent = currentSlideIndex + 1;
}

// Keyboard navigation for carousel
document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowLeft') {
        changeSlide(-1);
    } else if (e.key === 'ArrowRight') {
        changeSlide(1);
    }
});

// Function to ask a question via API
async function askQuestion(questionType) {
    // Update current question
    currentQuestion = questionType;
    
    // Update button states
    updateButtonStates(questionType);
    
    // Show loading state
    showLoading(questionType);
    
    try {
        if (USE_STREAMING) {
            // Use streaming API
            await streamAnswer(questionType);
        } else {
            // Call regular API
            const answer = await callAPI(questionType);
            displayAnswer(questionType, answer);
        }
        
    } catch (error) {
        console.error('Error calling API:', error);
        // Fallback to hardcoded answers
        fallbackToHardcoded(questionType);
    }
}

// Stream answer from API
async function streamAnswer(questionType) {
    const questionText = QUESTION_TEXTS[questionType];
    const answerText = document.getElementById('answerText');
    
    try {
        const response = await fetch(API_STREAM_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                property_url: PROPERTY_URL,
                question: questionText
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullAnswer = '';
        
        answerText.innerHTML = '';
        answerText.style.opacity = '1';
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    
                    if (data.type === 'answer') {
                        fullAnswer += data.data;
                        // Update display with current text
                        answerText.innerHTML = formatMarkdownToHTML(fullAnswer);
                        // Scroll to bottom
                        answerText.scrollTop = answerText.scrollHeight;
                    }
                }
            }
        }
        
        // Show "other questions" after completion
        if (!hasShownAnswer) {
            hasShownAnswer = true;
            const otherQuestions = document.getElementById('otherQuestions');
            if (otherQuestions) {
                otherQuestions.style.display = 'block';
            }
        }
        
    } catch (error) {
        throw error;
    }
}

// Call API
async function callAPI(questionType) {
    const questionText = QUESTION_TEXTS[questionType];
    
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            property_url: PROPERTY_URL,
            question: questionText
        })
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.answer;
}

// Show loading state
function showLoading(questionType) {
    const answerSection = document.getElementById('answerSection');
    const answerQuestion = document.getElementById('answerQuestion');
    const answerText = document.getElementById('answerText');
    
    const questionEmoji = {
        'can_i_own': '❓',
        'lease_works': '🏠',
        'is_safe': '✅',
        'costs': '💰'
    };
    
    answerQuestion.textContent = `${questionEmoji[questionType]} ${QUESTION_TEXTS[questionType]}`;
    answerText.innerHTML = '<p style="color: #6B7280;">Loading answer...</p>';
    
    answerSection.style.display = 'block';
    answerSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display answer with streaming effect
function displayAnswer(questionType, answer) {
    const answerText = document.getElementById('answerText');
    
    // Convert markdown to HTML
    let formattedAnswer = formatMarkdownToHTML(answer);
    
    // Show answer with typing effect
    answerText.innerHTML = '';
    streamText(answerText, formattedAnswer);
    
    // Show "other questions" section after first answer
    if (!hasShownAnswer) {
        hasShownAnswer = true;
        const otherQuestions = document.getElementById('otherQuestions');
        if (otherQuestions) {
            otherQuestions.style.display = 'block';
        }
    }
}

// Convert markdown to HTML
function formatMarkdownToHTML(text) {
    return text
        // Headers
        .replace(/### (.*?)(\n|$)/g, '<h4>$1</h4>')
        .replace(/## (.*?)(\n|$)/g, '<h3>$1</h3>')
        .replace(/# (.*?)(\n|$)/g, '<h3>$1</h3>')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Numbered lists
        .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
        // Bullet lists
        .replace(/^[-•]\s+(.+)$/gm, '<li>$1</li>')
        // Wrap consecutive <li> in <ul>
        .replace(/(<li>.*?<\/li>\n?)+/g, '<ul>$&</ul>')
        // Paragraphs
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        // Wrap in paragraph if not already wrapped
        .replace(/^(?!<[uh])/gm, '<p>')
        .replace(/(?<!>)$/gm, '</p>')
        // Clean up
        .replace(/<p><\/p>/g, '')
        .replace(/<p>(<[uh])/g, '$1')
        .replace(/(<\/[uh][^>]*>)<\/p>/g, '$1');
}

// Stream text with typing effect
function streamText(element, html) {
    // For now, show immediately (streaming from OpenAI would require backend changes)
    element.innerHTML = html;
    
    // TODO: Implement real streaming when backend supports it
    // For now, just show with fade-in animation
    element.style.opacity = '0';
    setTimeout(() => {
        element.style.transition = 'opacity 0.3s';
        element.style.opacity = '1';
    }, 50);
}

// Fallback to hardcoded answers if API fails
function fallbackToHardcoded(questionType) {
    const answerData = ANSWERS[questionType];
    
    if (!answerData) {
        console.error('Answer not found for question:', questionType);
        return;
    }
    
    const answerText = document.getElementById('answerText');
    answerText.innerHTML = answerData.content;
    
    // Show "other questions" section after first answer
    if (!hasShownAnswer) {
        hasShownAnswer = true;
        const otherQuestions = document.getElementById('otherQuestions');
        if (otherQuestions) {
            otherQuestions.style.display = 'block';
        }
    }
}

// Function to close answer
function closeAnswer() {
    const answerSection = document.getElementById('answerSection');
    answerSection.style.display = 'none';
    
    // Reset button states
    const questionButtons = document.querySelectorAll('.question-btn');
    questionButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    currentQuestion = null;
}

// Function to ask custom question
async function askCustomQuestion() {
    const input = document.getElementById('customQuestionInput');
    const customQuestion = input.value.trim();
    
    if (!customQuestion) {
        alert('Please enter a question');
        return;
    }
    
    // Disable input while processing
    input.disabled = true;
    const btn = document.querySelector('.custom-question-btn');
    btn.disabled = true;
    btn.textContent = 'Loading...';
    
    // Clear button states
    const questionButtons = document.querySelectorAll('.question-btn');
    questionButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    // Show loading
    const answerSection = document.getElementById('answerSection');
    const answerQuestion = document.getElementById('answerQuestion');
    const answerText = document.getElementById('answerText');
    
    answerQuestion.textContent = `❓ ${customQuestion}`;
    answerText.innerHTML = '<p style="color: #6B7280;">Loading answer...</p>';
    answerSection.style.display = 'block';
    answerSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    try {
        if (USE_STREAMING) {
            // Stream custom answer
            await streamCustomAnswer(customQuestion);
        } else {
            // Call API with custom question
            const answer = await callCustomAPI(customQuestion);
            answerText.innerHTML = formatMarkdownToHTML(answer);
        }
        
        // Show "other questions" after first answer
        if (!hasShownAnswer) {
            hasShownAnswer = true;
            const otherQuestions = document.getElementById('otherQuestions');
            if (otherQuestions) {
                otherQuestions.style.display = 'block';
            }
        }
        
    } catch (error) {
        console.error('Error asking custom question:', error);
        console.error('Full error:', error.message, error.stack);
        answerText.innerHTML = '<p style="color: #DC2626;">Sorry, there was an error processing your question. Please try again or contact the agent directly.</p>';
    } finally {
        // Re-enable input
        input.disabled = false;
        input.value = '';
        btn.disabled = false;
        btn.textContent = 'Ask →';
    }
}

// Stream custom answer
async function streamCustomAnswer(question) {
    const answerText = document.getElementById('answerText');
    
    try {
        const response = await fetch(API_STREAM_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                property_url: PROPERTY_URL,
                question: question
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullAnswer = '';
        
        answerText.innerHTML = '';
        answerText.style.opacity = '1';
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    
                    if (data.type === 'answer') {
                        fullAnswer += data.data;
                        answerText.innerHTML = formatMarkdownToHTML(fullAnswer);
                        answerText.scrollTop = answerText.scrollHeight;
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Error in streamCustomAnswer:', error);
        console.error('Error details:', error.message, error.stack);
        throw error;
    }
}

// Call API with custom question
async function callCustomAPI(question) {
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            property_url: PROPERTY_URL,
            question: question
        })
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.answer;
}

// Function to update button states
function updateButtonStates(activeQuestionType) {
    const questionButtons = document.querySelectorAll('.question-btn');
    questionButtons.forEach(button => {
        const questionType = button.getAttribute('data-question');
        if (questionType === activeQuestionType) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

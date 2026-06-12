import time

def generate_response(question: str) -> str:
    """
    Mock LLM response for testing purposes without needing OpenAI API keys.
    """
    # Simulate processing time
    time.sleep(1.0)
    
    responses = {
        "hello": "Hello there! I am an AI agent. How can I help you?",
        "test": "This is a test response.",
        "what is docker": "Docker is a platform for developing, shipping, and running applications in containers.",
    }
    
    question_lower = question.lower()
    for key, val in responses.items():
        if key in question_lower:
            return val
            
    return f"I am a mock LLM. I received your question: '{question}'. My context is limited."

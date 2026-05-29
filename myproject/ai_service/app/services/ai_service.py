import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class AIService:
    API_KEY = os.getenv("AI_API_KEY", "your-api-key-here")
    # For demonstration, using a generic API call structure (compatible with Gemini or OpenAI)
    # Here we assume an endpoint URL for a LLM
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    @classmethod
    def call_llm(cls, prompt):
        """Helper to call LLM API"""
        if cls.API_KEY == "your-api-key-here":
            return f"AI Response to: {prompt[:50]}... (API Key not configured)"
            
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                response = requests.post(f"{cls.API_URL}?key={cls.API_KEY}", json=payload, headers=headers)
                
                if response.status_code == 429:
                    wait_time = (attempt + 1) * 5
                    print(f"Rate limited, retrying in {wait_time}s... (attempt {attempt+1})")
                    time.sleep(wait_time)
                    continue
                
                result = response.json()
                
                if 'error' in result:
                    return f"AI error: {result['error'].get('message', 'Unknown error')}"
                
                # Extract text from Gemini response - get the last part (skip thinking tokens)
                candidates = result.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    # Return the last text part (gemini-2.5-flash may include thinking parts)
                    for part in reversed(parts):
                        if 'text' in part:
                            return part['text']
                
                return "AI không thể tạo câu trả lời."
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return f"Error calling AI: {str(e)}"
        return "AI đang bận, vui lòng thử lại sau."

    @classmethod
    def explain_concept(cls, concept, level="intermediate"):
        prompt = f"Explain the concept of '{concept}' at a {level} level for a student. Provide examples and a structured explanation."
        return cls.call_llm(prompt)

    @classmethod
    def summarize_document(cls, doc_content):
        prompt = f"Summarize the following course material, extract key points, and list important definitions:\n\n{doc_content}"
        return cls.call_llm(prompt)

    @classmethod
    def answer_question(cls, context, question):
        prompt = f"Based on the following course material:\n{context}\n\nAnswer this student question: {question}"
        return cls.call_llm(prompt)

    @classmethod
    def generate_practice_questions(cls, topic, difficulty="medium", count=5):
        prompt = f"Generate {count} {difficulty} level practice questions (multiple choice and short answer) about {topic}. Include correct answers."
        return cls.call_llm(prompt)

    @classmethod
    def get_study_recommendations(cls, student_performance_summary):
        prompt = f"Analyze the following student performance summary and suggest topics for revision and recommended exercises:\n{student_performance_summary}"
        return cls.call_llm(prompt)

import asyncio
import time
import json
from typing import Dict, Any, List
import openai
from openai import AsyncOpenAI

from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            print("Warning: OpenAI API key not provided, using mock responses")
    
    async def generate_quiz_from_text(self, text: str, num_questions: int = 5) -> Dict[str, Any]:
        """Generate quiz questions from text using OpenAI"""
        start_time = time.time()
        
        if not self.client:
            # Mock response for development
            await asyncio.sleep(2)  # Simulate API call time
            return self._generate_mock_quiz(text, num_questions, start_time)
        
        try:
            prompt = self._create_quiz_prompt(text, num_questions)
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational assistant that creates quiz questions from text. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            quiz_data = json.loads(content)
            
            processing_time = time.time() - start_time
            
            return {
                "questions": quiz_data.get("questions", []),
                "generation_time": processing_time
            }
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI response as JSON: {e}")
            return self._generate_mock_quiz(text, num_questions, start_time)
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_mock_quiz(text, num_questions, start_time)
    
    def _create_quiz_prompt(self, text: str, num_questions: int) -> str:
        """Create prompt for quiz generation"""
        return f"""
        Based on the following text, create {num_questions} multiple-choice questions. 
        Each question should have 4 options (A, B, C, D) with one correct answer.
        
        Text: {text}
        
        Please respond with a JSON object in this exact format:
        {{
            "questions": [
                {{
                    "question": "Question text here?",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct_answer": "A",
                    "explanation": "Brief explanation of why this is correct"
                }}
            ]
        }}
        
        Make sure the questions test understanding of the key concepts in the text.
        """
    
    def _generate_mock_quiz(self, text: str, num_questions: int, start_time: float) -> Dict[str, Any]:
        """Generate mock quiz for development/fallback"""
        mock_questions = []
        
        for i in range(num_questions):
            mock_questions.append({
                "question": f"Sample question {i+1} based on the provided text?",
                "options": [
                    f"A) Sample option A for question {i+1}",
                    f"B) Sample option B for question {i+1}",
                    f"C) Sample option C for question {i+1}",
                    f"D) Sample option D for question {i+1}"
                ],
                "correct_answer": "A",
                "explanation": f"This is a sample explanation for question {i+1}"
            })
        
        processing_time = time.time() - start_time
        
        return {
            "questions": mock_questions,
            "generation_time": processing_time
        }
    
    async def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment for safety monitoring"""
        if not self.client:
            return {"sentiment": "neutral", "confidence": 0.5}
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the sentiment of the following text. Respond with JSON containing 'sentiment' (positive/negative/neutral) and 'confidence' (0-1)."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return {
                "sentiment": result.get("sentiment", "neutral"),
                "confidence": result.get("confidence", 0.5)
            }
            
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "confidence": 0.5}
    
    def generate_quiz_sync(self, text: str, num_questions: int = 5) -> Dict[str, Any]:
        """Synchronous version for worker processes"""
        start_time = time.time()
        
        if not self.client:
            time.sleep(2)  # Simulate processing time
            return self._generate_mock_quiz(text, num_questions, start_time)
        
        try:
            # Use synchronous OpenAI client for worker
            sync_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = self._create_quiz_prompt(text, num_questions)
            
            response = sync_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational assistant that creates quiz questions from text. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            quiz_data = json.loads(content)
            
            processing_time = time.time() - start_time
            
            return {
                "questions": quiz_data.get("questions", []),
                "generation_time": processing_time
            }
            
        except Exception as e:
            print(f"Quiz generation error: {e}")
            return self._generate_mock_quiz(text, num_questions, start_time)
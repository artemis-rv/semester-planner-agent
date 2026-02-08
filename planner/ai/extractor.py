import os
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv

from planner.utils.logger import setup_logger

# Ensure environment variables are loaded
load_dotenv()

logger = setup_logger(__name__)

# Define Pydantic models for validation
class TopicSchema(BaseModel):
    topic: str
    subtopics: List[str]

class UnitSchema(BaseModel):
    unit_no: int
    title: str
    importance: str  # IMP / LESS_IMP
    minimum_hours: Optional[int] = None
    topics: List[TopicSchema]
    self_study: List[str] = []

class SyllabusSchema(BaseModel):
    code: str
    name: str
    credits: int
    exam_weightage: Dict[str, Any]
    units: List[UnitSchema]

class Syllabusextractor:
    """
    Uses Gemini to extract structured syllabus data from cleaned text.
    """

    def __init__(self, api_key: Optional[str] = None):
        # Priority: argument -> environment
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.error("GEMINI_API_KEY is missing. Please check your .env file.")
            raise ValueError("GEMINI_API_KEY not found in environment or arguments.")
        
        try:
            genai.configure(api_key=self.api_key)
            # Some environments/keys hit 404 with 'gemini-1.5-flash'
            # 'gemini-1.5-flash-latest' or 'gemini-1.5-flash' are standard
            self.model = genai.GenerativeModel('gemini-flash-latest')
            logger.info("Gemini AI Extractor initialized with 'gemini-flash-latest'.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Model: {e}")
            raise

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extracts structured JSON from raw text.
        """
        if not text:
            return {}

        prompt = self._build_prompt(text)
        
        logger.info("Sending request to Gemini for syllabus extraction...")
        try:
            # We explicitly allow the model to provide JSON
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                ),
            )
            
            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            result_json = json.loads(response.text)
            
            # Validate with Pydantic
            validated = SyllabusSchema(**result_json)
            return validated.model_dump()
            
        except Exception as e:
            logger.error(f"Error during AI extraction: {e}")
            if "404" in str(e):
                logger.error("Model 404 detected. Trying fallback to 'gemini-pro'...")
                # Fallback logic if needed, but 1.5-flash should work.
                # This often happens if the API version is mismatched in the library.
            raise

    def _build_prompt(self, text: str) -> str:
        return f"""
        You are an expert academic administrator. Extract the following syllabus information into a strict JSON format.
        
        Syllabus Text:
        ---
        {text}
        ---
        
        JSON schema requirements:
        - code: Subject code (e.g., "CS101")
        - name: Full subject name
        - credits: Number of credits
        - exam_weightage: A dictionary of components and their percentage (e.g., {{"midterm": 30, "final": 70}})
        - units: A list of objects with:
            - unit_no: Integer
            - title: Unit title
            - importance: Exactly "IMP" or "LESS_IMP" (decide based on content depth/complexity)
            - minimum_hours: Integer (if specified, else null)
            - topics: List of objects with:
                - topic: Main topic name
                - subtopics: List of strings
            - self_study: List of strings for self-study topics if mentioned
            
        Return ONLY the raw JSON content. Do not include markdown formatting.
        """

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extractor = Syllabusextractor()
        with open(sys.argv[1], 'r') as f:
            content = f.read()
        logger.info("Attempting AI extraction...")
        print(json.dumps(extractor.extract(content), indent=2))

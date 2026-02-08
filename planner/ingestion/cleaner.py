import re
import os
from typing import List
from planner.utils.logger import setup_logger

logger = setup_logger(__name__)

class SyllabusCleaner:
    """
    Cleans and normalizes raw text extracted from syllabus documents.
    """

    def clean(self, text: str) -> str:
        """
        Main method to clean text.
        """
        if not text:
            return ""

        logger.info("Starting text cleaning process...")
        text = self.remove_junk(text)
        text = self.normalize_bullets(text)
        text = self.normalize_spacing(text)
        text = self.preserve_structural_markers(text)
        
        return text.strip()

    def remove_junk(self, text: str) -> str:
        """
        Removes headers, footers, page numbers, and common noise.
        """
        # Remove page numbers (e.g., "Page 1 of 10", "1 | Page", "[1]")
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d+\s+\|\s+Page', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\d+\]', '', text)
        
        # Remove repeated non-alphanumeric patterns (often borders/separators)
        text = re.sub(r'[-=_]{3,}', '\n', text)
        
        return text

    def normalize_bullets(self, text: str) -> str:
        """
        Standardizes various bullet point formats to a single pattern.
        """
        # Replace common bullets (o, *, -, >) followed by space with a standard '-'
        text = re.sub(r'^\s*[\u2022\u002A\u002D\u003E]\s*', '- ', text, flags=re.MULTILINE)
        
        # Handle numbered bullets (1., 1.1, (i), a))
        text = re.sub(r'^\s*(\d+(\.\d+)*|[a-zA-Z]\)|[ivxIVX]+\))\s*', r'\1 ', text, flags=re.MULTILINE)
        
        return text

    def normalize_spacing(self, text: str) -> str:
        """
        Fixes excessive newlines and whitespace.
        """
        # Collapse multiple newlines into double newlines (paragraph separation)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove trailing spaces on each line
        text = "\n".join(line.rstrip() for line in text.splitlines())
        return text

    def preserve_structural_markers(self, text: str) -> str:
        """
        Ensures structural keywords are prominent.
        """
        keywords = ["Unit", "Chapter", "Importance", "Hours", "Topic", "Subject", "Module"]
        for kw in keywords:
            # Ensure keyword at start of line has a newline before it if not already there
            # Using raw strings to avoid SyntaxWarning
            text = re.sub(rf'(?<!\n\n)({kw}\s+\d+:)', r'\n\n\1', text, flags=re.IGNORECASE)
            text = re.sub(rf'(?<!\n\n)({kw}\s+[I|V|X]+:)', r'\n\n\1', text, flags=re.IGNORECASE)
            
        return text

if __name__ == "__main__":
    # Example usage for testing
    cleaner = SyllabusCleaner()
    sample = """
    Page 1 of 2
    Syllabus: Computer Networks
    --------------------------
    
    Unit 1: Introduction (10 Hours)
    * OSI Model
    * TCP/IP Suite
    """
    logger.info("Running sample clean...")
    print(cleaner.clean(sample))

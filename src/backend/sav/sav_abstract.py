from abc import ABC, abstractmethod
from typing import NamedTuple


class RecodeResult(NamedTuple):
    """Result from generating SPSS recode script"""
    script: str
    matched: list[tuple[str, str]]
    unmatched: list[tuple[str, str]]


class SavProcessor(ABC):
    """Abstract base class for SAV file processing"""
    
    @abstractmethod
    def generate_recode_script(
        self, 
        plaintiff_questions: list[str], 
        defense_questions: list[str], 
        recode_settings: dict[str, dict[str, int]]
    ) -> RecodeResult:
        """
        Generate SPSS syntax to recode questions.
        
        Args:
            plaintiff_questions: List of plaintiff question texts
            defense_questions: List of defense question texts
            recode_settings: Dictionary mapping questions to their recode settings
            
        Returns:
            RecodeResult containing:
                - script: SPSS syntax string
                - matched: List of (category, question) tuples that were matched
                - unmatched: List of (category, question) tuples that weren't matched
        """
        pass
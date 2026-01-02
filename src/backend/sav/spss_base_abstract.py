"""Abstract base class for SPSS SAV file processing"""
from abc import ABC, abstractmethod
from typing import NamedTuple


class SPSSResult(NamedTuple):
    """Result from SPSS processing operations"""
    matched: list[tuple[str, str]]  # List of (category, question) that matched
    unmatched: list[tuple[str, str]]  # List of (category, question) that didn't match


class SPSSProcessor(ABC):
    """
    Abstract base class for SAV file processing.
    
    Provides core functionality for reading SAV files and matching questions
    with variable labels. Subclasses implement specific operations like
    syntax generation, reporting, or data export.
    """
    
    def __init__(self, sav_labels: list[tuple[str, str]], name1: str, name2: str):
        """
        Initialize SPSS processor.
        
        Args:
            sav_labels: List of (column_name, label) tuples from SAV file
            name1: First party name (e.g., 'Plaintiff', 'Wine Warehouse')
            name2: Second party name (e.g., 'Defense', 'Golden State Cider')
        """
        self._sav_labels = sav_labels
        self._name1 = name1
        self._name2 = name2
        self._label_to_column = self._build_label_mapping()
        self._matched: list[tuple[str, str]] = []
        self._unmatched: list[tuple[str, str]] = []
    
    @abstractmethod
    def _build_label_mapping(self) -> dict[str, str]:
        """
        Convert SAV labels into a dictionary for quick lookup.
        
        Returns:
            Dictionary mapping label (question text) to column name
            Example: {"Do you think bob ate cookie": "Q32"}
        """
        pass
    
    @abstractmethod
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent matching.
        
        Handles whitespace, hyphens, etc.
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text for comparison
        """
        pass
    
    @abstractmethod
    def _find_column(self, question: str) -> str | None:
        """
        Find SAV column name by matching question text.
        
        Tries exact match first, then partial matches.
        
        Args:
            question: The question text to find (e.g., "Do you think Bob ate the cookie")
            
        Returns:
            Column name if found (e.g., "Q32"), None otherwise
        """
        pass
    @abstractmethod
    def get_all_general_question(self,name1: str = "Plaaffs",name2:str = "Defaffs") -> list [tuple[str,str]]:
        "get a list of all of the questions not part of the Plaaffs or Defaffs"
        pass
    def get_matched_questions(self) -> list[tuple[str, str]]:
        """
        Get list of successfully matched questions.
        
        Returns:
            List of (category, question) tuples that were matched
        """
        return self._matched.copy()
    
    def get_unmatched_questions(self) -> list[tuple[str, str]]:
        """
        Get list of questions that couldn't be matched.
        
        Returns:
            List of (category, question) tuples that weren't found in SAV
        """
        return self._unmatched.copy()
    
    def get_result(self) -> SPSSResult:
        """
        Get processing result with matched and unmatched questions.
        
        Returns:
            SPSSResult named tuple with matched and unmatched lists
        """
        return SPSSResult(
            matched=self._matched.copy(),
            unmatched=self._unmatched.copy()
        )
    
    def reset_tracking(self) -> None:
        """Reset matched/unmatched tracking for new processing run"""
        self._matched = []
        self._unmatched = []
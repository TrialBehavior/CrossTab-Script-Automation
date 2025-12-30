"""Concrete implementation of SPSSProcessor with matching logic"""
import re
from .Spss_base_abstract import SPSSProcessor, SPSSResult


class SPSSMatchProcessor(SPSSProcessor):
    """
    Concrete SPSS processor that handles question matching.
    
    Provides the core matching functionality using your existing logic
    for text normalization and column finding.
    """
    
    def _build_label_mapping(self) -> dict[str, str]:
        """
        Build mapping from labels to column names.
        
        Returns:
            Dictionary mapping label to column name
        """
        mapping: dict[str, str] = {}
        for column, label in self._sav_labels:
            mapping[label] = column
        return mapping
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize whitespace and hyphens for consistent matching.
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text
        """
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces -> single space
        text = re.sub(r'-\s+', '-', text)  # Space after hyphen -> no space
        text = re.sub(r'\s+-', '-', text)  # Space before hyphen -> no space
        return text.strip()
    
    def _find_column(self, question: str) -> str | None:
        """
        Find column by exact match or partial match.
        
        Args:
            question: The question text to search for
            
        Returns:
            Column name if found, None otherwise
        """
        # Try exact match first
        if question in self._label_to_column:
            return self._label_to_column[question]
        
        # Try partial match
        normalized_question = self._normalize_text(question)
        for label, column in self._label_to_column.items():
            if normalized_question in self._normalize_text(label):
                return column
        
        return None
    
    def find_all_matches(
        self, 
        name1_questions: list[str], 
        name2_questions: list[str]
    ) -> SPSSResult:
        """
        Find matches for all questions and track results.
        
        Args:
            name1_questions: Questions from first party
            name2_questions: Questions from second party
            
        Returns:
            SPSSResult with matched and unmatched questions
        """
        self.reset_tracking()
        
        # Process name1 questions
        for question in name1_questions:
            column = self._find_column(question)
            if column:
                self._matched.append((self._name1, question))
            else:
                self._unmatched.append((self._name1, question))
        
        # Process name2 questions
        for question in name2_questions:
            column = self._find_column(question)
            if column:
                self._matched.append((self._name2, question))
            else:
                self._unmatched.append((self._name2, question))
        
        return self.get_result()
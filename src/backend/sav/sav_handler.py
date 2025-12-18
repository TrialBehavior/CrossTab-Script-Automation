import re
from .sav_abstract import SavProcessor, RecodeResult


class SavHandler(SavProcessor):
    """Handles SAV file processing and SPSS syntax generation"""
    
    def __init__(self, sav: list[tuple[str, str]]):
        """
        Initialize the SAV handler.
        
        Args:
            sav: List of tuples containing (column, label) pairs
        """
        self.sav = sav
        self.label_to_column = self._build_label_mapping()
        
        # Results storage
        self._script: str = ""
        self._matched: list[tuple[str, str]] = []
        self._unmatched: list[tuple[str, str]] = []
    
    def _build_label_mapping(self) -> dict[str, str]:
        """Build mapping from labels to column names"""
        mapping: dict[str, str] = {}
        for column, label in self.sav:
            mapping[label] = column
        return mapping
    
    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace and hyphens for consistent matching"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'-\s+', '-', text)
        text = re.sub(r'\s+-', '-', text)
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
        if question in self.label_to_column:
            return self.label_to_column[question]
        
        # Try partial match
        normalized_question = self._normalize_text(question)
        for label, column in self.label_to_column.items():
            if normalized_question in self._normalize_text(label):
                return column
        
        return None
    
    def _generate_recode_syntax(
        self, 
        column: str, 
        question: str, 
        settings: dict[str, int]
    ) -> str:
        """
        Generate SPSS recode syntax for a single question.
        
        Args:
            column: Column name to recode
            question: Question text for label
            settings: Dictionary containing recode range settings
            
        Returns:
            SPSS syntax string
        """
        return (
            f"recode {column} "
            f"({settings['range1_start']} thru {settings['range1_end']}={settings['range1_becomes']}) "
            f"({settings['range2_start']} thru {settings['range2_end']}={settings['range2_becomes']}) "
            f"into {column}r.\n"
            f"variable labels {column}r '{question}'.\n"
            f"value labels {column}r 1 'Plaintiff' 2 'Defense'.\n"
            f"execute.\n\n"
        )
    
    def _process_questions(
        self, 
        questions: list[str], 
        category: str, 
        recode_settings: dict[str, dict[str, int]]
    ) -> None:
        """
        Process a list of questions for a given category.
        
        Args:
            questions: List of question texts
            category: Either 'Plaintiff' or 'Defense'
            recode_settings: Dictionary of recode settings per question
        """
        for question in questions:
            column = self._find_column(question)
            
            if column and question in recode_settings:
                syntax = self._generate_recode_syntax(column, question, recode_settings[question])
                self._script += syntax
                self._matched.append((category, question))
            else:
                self._unmatched.append((category, question))
    
    def generate_recode_script(
        self, 
        plaintiff_questions: list[str], 
        defense_questions: list[str], 
        recode_settings: dict[str, dict[str, int]]
    ) -> RecodeResult:
        """
        Generate SPSS syntax to recode questions based on their labels.
        Uses per-question recode settings with customizable ranges.
        
        Args:
            plaintiff_questions: List of plaintiff question texts
            defense_questions: List of defense question texts
            recode_settings: Dictionary mapping questions to their recode settings
            
        Returns:
            RecodeResult with script, matched questions, and unmatched questions
        """
        # Reset results
        self._script = ""
        self._matched = []
        self._unmatched = []
        
        # Process both question sets
        self._process_questions(plaintiff_questions, 'Plaintiff', recode_settings)
        self._process_questions(defense_questions, 'Defense', recode_settings)
        
        return RecodeResult(
            script=self._script,
            matched=self._matched,
            unmatched=self._unmatched
        )
    
    def get_matched_questions(self) -> list[tuple[str, str]]:
        """Get list of successfully matched questions"""
        return self._matched.copy()
    
    def get_unmatched_questions(self) -> list[tuple[str, str]]:
        """Get list of questions that couldn't be matched"""
        return self._unmatched.copy()
    
    def get_script(self) -> str:
        """Get the generated SPSS script"""
        return self._script
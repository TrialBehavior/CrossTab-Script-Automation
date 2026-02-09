from typing import NamedTuple
from .spss_match_processor import SPSSMatchProcessor


class RecodeResult(NamedTuple):
    """Result from generating SPSS recode script"""
    script: str
    matched: list[tuple[str, str]]
    unmatched: list[tuple[str, str]]


class SPSSSyntaxGenerator(SPSSMatchProcessor):
    """
    SPSS syntax generator that inherits matching logic.
    
    This is a refactored version of your SavHandler that separates
    the matching logic (in SPSSMatchProcessor) from the syntax
    generation logic (in this class).
    """
    
    def __init__(self, sav_labels: list[tuple[str, str]], name1: str = "Plaintiff", name2: str = "Defense"):
        """
        Initialize syntax generator.
        
        Args:
            sav_labels: List of (column_name, label) tuples from SAV file
            name1: First party name (default: "Plaintiff")
            name2: Second party name (default: "Defense")
        """
        super().__init__(sav_labels, name1, name2)
        self._script = ""
    
    def generate_recode_script(
        self,
        name1_questions: list[str],
        name2_questions: list[str],
        recode_settings: dict[str, dict[str, int]]
    ) -> RecodeResult:
        """
        Generate SPSS syntax to recode questions based on their labels.
        Uses per-question recode settings with customizable ranges.
        
        Args:
            name1_questions: List of first party question texts
            name2_questions: List of second party question texts
            recode_settings: Dictionary mapping questions to their recode settings
            
        Returns:
            RecodeResult with script, matched questions, and unmatched questions
        """
        # Reset results
        self._script = ""
        self.reset_tracking()
        
        # Process both question sets
        self._process_questions(name1_questions, self._name1, recode_settings)
        self._process_questions(name2_questions, self._name2, recode_settings)
        
        return RecodeResult(
            script=self._script,
            matched=self._matched,
            unmatched=self._unmatched
        )
    
    def _process_questions(self, questions: list[str], category: str, recode_settings: dict[str, dict[str, int]]) -> None:
        """
        Process a list of questions for a given category.
        
        Args:
            questions: List of question texts
            category: Party name (e.g., 'Plaintiff', 'Defense')
            recode_settings: Dictionary of recode settings per question
        """
        for question in questions:
            # Check if this is a neutral question (has matched_column already)
            if question in recode_settings and recode_settings[question].get('matched_column'):
                # For neutral questions, column is already known
                column = recode_settings[question]['matched_column']
            else:
                # For plaintiff/defense questions, find the column
                column = self._find_column(question)
            
            if column and question in recode_settings:
                syntax = self._generate_recode_syntax(column, question, recode_settings[question])
                self._script += syntax
                self._matched.append((category, question))
            else:
                self._unmatched.append((category, question))
    
    def _generate_recode_syntax(self, column: str, question: str, settings: dict[str, int]) -> str:
        """Generate SPSS recode syntax for a single question"""
        
        variable_type = settings.get('variable_type', 'categorical')
        
        if variable_type == 'continuous':
            # Continuous variable syntax
            range1 = self._operator_to_spss_range(
                settings['range1_operator'], 
                settings['range1_value']
            )
            range2 = self._operator_to_spss_range(
                settings['range2_operator'],
                settings['range2_value']
            )
            
            return (
                f"recode {column} "
                f"({range1}={settings['range1_becomes']}) "
                f"({range2}={settings['range2_becomes']}) "
                f"into {column}.r\n"
                f"variable labels {column}r '{question}'.\n"
                f"value labels {column}r 1 '{self._name1}' 2 '{self._name2}'.\n"
                f"execute.\n\n"
            )
        else:
            # Categorical variable syntax (existing)
            return (
                f"recode {column} "
                f"({settings['range1_start']} thru {settings['range1_end']}={settings['range1_becomes']}) "
                f"({settings['range2_start']} thru {settings['range2_end']}={settings['range2_becomes']}) "
                f"into {column}.r\n"
                f"variable labels {column}r '{question}'.\n"
                f"value labels {column}r 1 '{self._name1}' 2 '{self._name2}'.\n"
                f"execute.\n\n"
            )

    def _operator_to_spss_range(self, operator: str, value: float) -> str:
        """Convert operator and value to SPSS range syntax"""
        if operator == '<':
            return f"LOWEST thru {value - 0.01}"
        elif operator == '<=':
            return f"LOWEST thru {value}"
        elif operator == '=':
            return f"{value}"
        elif operator == '>=':
            return f"{value} thru HIGHEST"
        elif operator == '>':
            return f"{value + 0.01} thru HIGHEST"
        return str(value)
    
    def get_script(self) -> str:
        """Get the generated SPSS script"""
        return self._script
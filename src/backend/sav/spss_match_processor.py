"""Concrete implementation of SPSSProcessor with matching logic"""
import re
import pyreadstat
from .spss_base_abstract import SPSSProcessor, SPSSResult
import io


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
    def get_all_general_questions(self, name1: str = "Plaaffs", name2: str = "Defaffs") -> list[tuple[str, str]]:
        """
        Get all general questions (questions before party-specific questions).
        
        Args:
            name1: First party identifier (default "Plaaffs")
            name2: Second party identifier (default "Defaffs")
            
        Returns:
            List of tuples (column_name, label)
            example: [("Q1", "How satisfied are you?"), ("Q2", "Please enter your age")]
        """
        general_questions = []
        
        # Text patterns to exclude (check in label text)
        text_input_patterns = [
            'first name',
            'last name',
            'firstname', 
            'lastname',
            'enter your name',
            'please enter',
            'please type',
            'address',
            'email',
            'phone',
            'zip code',
            'zipcode',
            'city',
            'state',
            'comments'
        ]
        
        # Metadata fields to exclude (check in column names)
        metadata_columns = {
            'firstname',
            'lastname', 
            'first_name',
            'last_name',
            'j_number',
            'final_leaning',
            'email',
            'phone',
            'address',
            'zipcode',
            'zip_code'
        }
        
        for column, label in self._sav_labels:
            if label is None:
                break
            # Lowercase for comparison 
            col_lower = column.lower()
            label_lower = label.lower()
            
            # Check if this column is a party-specific question (stops at first match)
            if name1.lower() in col_lower or name2.lower() in col_lower:
                break
            
            # Check if column name matches metadata patterns
            if col_lower in metadata_columns:
                continue
            
            # Check if label contains text input patterns
            skip = False
            for pattern in text_input_patterns:
                if pattern in label_lower:
                    skip = True
                    break
            
            if skip:
                continue
            
            # Add to general questions
            general_questions.append((column, label))
        
        return general_questions
    @staticmethod
    def get_essentials_from_sav(sav_file, name1: str, name2: str) -> dict:
        """
        Extract essential data from SAV file for SPSS processing.
        
        Args:
            sav_file: Uploaded SAV file (file-like object or path)
            name1: First party name
            name2: Second party name
            
        Returns:
            Dictionary containing df, meta, sav_labels, and names
        """
        import pyreadstat
        import tempfile
        import os
        
        # Handle UploadedFile objects - save to temp file
        if hasattr(sav_file, 'read'):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.sav') as tmp_file:
                tmp_file.write(sav_file.read())
                tmp_path = tmp_file.name
            
            # Read the SAV file from temp path
            df, meta = pyreadstat.read_sav(tmp_path)
            
            # Clean up temp file
            os.unlink(tmp_path)
        else:
            # It's already a path string
            df, meta = pyreadstat.read_sav(sav_file)
        
        # Extract sav_labels as list of (column_name, label) tuples
        sav_labels = []
        for col in df.columns:
            label = meta.column_names_to_labels.get(col, col)
            sav_labels.append((col, label))
        
        return {
            'df': df,
            'meta': meta,
            'sav_labels': sav_labels,
            'name1': name1,
            'name2': name2
        }
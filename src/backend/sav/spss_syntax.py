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
    Generates recode syntax including optional SYSMIS handling.
    """

    def __init__(self, sav_labels: list[tuple[str, str]], name1: str = "Plaintiff", name2: str = "Defense"):
        super().__init__(sav_labels, name1, name2)
        self._script = ""

    def generate_recode_script(self, name1_questions: list[str], name2_questions: list[str], recode_settings: dict[str, dict[str, int]]) -> RecodeResult:
        self._script = ""
        self.reset_tracking()

        self._process_questions(name1_questions, self._name1, recode_settings)
        self._process_questions(name2_questions, self._name2, recode_settings)

        neutral_questions = [
            label for label, settings in recode_settings.items()
            if settings.get('party') == 'neutral'
        ]
        self._process_questions(neutral_questions, 'Neutral', recode_settings)

        return RecodeResult(script=self._script, matched=self._matched, unmatched=self._unmatched)

    def _process_questions(self, questions: list[str], category: str, recode_settings: dict[str, dict[str, int]]) -> None:
        for question in questions:
            if question in recode_settings and recode_settings[question].get('matched_column'):
                column = recode_settings[question]['matched_column']
            else:
                column = self._find_column(question)

            if column and question in recode_settings:
                syntax = self._generate_recode_syntax(column, question, recode_settings[question])
                if syntax:
                    self._script += syntax
                    self._matched.append((category, question))
                else:
                    self._unmatched.append((category, question))
            else:
                self._unmatched.append((category, question))

    def _generate_recode_syntax(self, column: str, question: str, settings: dict[str, int]) -> str | None:
        """
        Generate SPSS recode syntax for a single question.
        Returns None if all ranges (including sysmis) map to None — nothing to generate.
        Adds (SYSMIS={value}) clause only when sysmis_becomes is explicitly set.
        """
        variable_type = settings.get('variable_type', 'categorical')
        r1_becomes = settings.get('range1_becomes')
        r2_becomes = settings.get('range2_becomes')
        sysmis_becomes = settings.get('sysmis_becomes')

        # Nothing to generate at all
        if r1_becomes is None and r2_becomes is None and sysmis_becomes is None:
            return None

        if variable_type == 'continuous':
            range1 = self._operator_to_spss_range(settings['range1_operator'], settings['range1_value'])
            range2 = self._operator_to_spss_range(settings['range2_operator'], settings['range2_value'])

            ranges = ""
            if r1_becomes is not None:
                ranges += f"({range1}={r1_becomes}) "
            if r2_becomes is not None:
                ranges += f"({range2}={r2_becomes}) "
            if sysmis_becomes is not None:
                ranges += f"(SYSMIS={sysmis_becomes}) "

            return (
                f"recode {column} {ranges.strip()} into {column}.r.\n"
                f"variable labels {column}.r '{question}'.\n"
                f"value labels {column}.r 1 '{self._name1}' 2 '{self._name2}'.\n"
                f"execute.\n\n"
            )
        else:
            ranges = ""
            if r1_becomes is not None:
                ranges += f"({settings['range1_start']} thru {settings['range1_end']}={r1_becomes}) "
            if r2_becomes is not None:
                ranges += f"({settings['range2_start']} thru {settings['range2_end']}={r2_becomes}) "
            if sysmis_becomes is not None:
                ranges += f"(SYSMIS={sysmis_becomes}) "

            return (
                f"recode {column} {ranges.strip()} into {column}.r.\n"
                f"variable labels {column}.r Recode: '{question}'.\n"
                f"value labels {column}.r 1 '{self._name1}' 2 '{self._name2}'.\n"
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
        return self._script
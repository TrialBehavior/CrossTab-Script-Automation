**Purpose Of This Script**
This is specifically for recoding the spss portion related to correlation crosstab. Work on the other ones are in the work! Essentially you upload the Posted Q4 pdf as well as the sav with all the survey's question. The script will then extract all of the text that our senior consultants have highlighted and from there a ui will popup allowing you to customize which numbers correlates with what.

<img width="881" height="269" alt="image" src="https://github.com/user-attachments/assets/c0d580d2-f8a8-4182-9ac8-8e397c32fef3" />




From there you then upload the spss related to the trial case so that the script can find the highlighted question within the spss and makes the recoding script.


<img width="742" height="140" alt="image" src="https://github.com/user-attachments/assets/29147e51-9b9b-4e88-b4a8-38b2f26ee78a" />


**Important To Notice**
This only extracts the questions from the plantiff and defense question. This means that you would have to still recode the general question for yourself. This was done as usually these questions are noted by a senior consultant through comments which currently can not be read through the pdf reader we use. Make sure to double check that all the highlighted questions from the pdf are included inside the rescript, the app will tell you which questions it could not extract to help you out.


# SPSS Processing Module — README

A three-layer class hierarchy for reading `.sav` files, matching survey questions to SPSS column names, and generating recode syntax scripts.

---

## Architecture Overview

```
SPSSProcessor (Abstract Base)
    └── SPSSMatchProcessor (Matching Logic)
            └── SPSSSyntaxGenerator (Syntax Generation)
```

---

## `spss_base_abstract.py` — `SPSSProcessor`

Abstract base class. Defines the interface and shared state all subclasses must implement.

---

### `SPSSResult` (NamedTuple)

A simple container returned by processing operations.

| Field | Type | Description |
|-------|------|-------------|
| `matched` | `list[tuple[str, str]]` | Questions that were found in the SAV file |
| `unmatched` | `list[tuple[str, str]]` | Questions that could not be matched |

Each tuple is `(category, question_text)`, e.g. `("Plaintiff", "Do you think the defendant was negligent?")`.

---

### `__init__(sav_labels, name1, name2)`

Initializes the processor with label data and party names.

**Input:**
- `sav_labels: list[tuple[str, str]]` — List of `(column_name, label)` pairs extracted from the SAV file. E.g. `[("Q1", "How old are you?"), ("Q32", "Do you think Bob ate the cookie?")]`
- `name1: str` — First party label, e.g. `"Plaintiff"` or `"Wine Warehouse"`
- `name2: str` — Second party label, e.g. `"Defense"` or `"Golden State Cider"`

**Sets up:** `_label_to_column` dict, empty `_matched` and `_unmatched` lists.

---

### `get_essentials_from_sav(sav_file, name1, name2)` *(static, abstract)*

Reads a `.sav` file and returns everything needed to construct a processor.

**Input:**
- `sav_file` — Either a file path string or an uploaded file object (e.g. Streamlit's `UploadedFile`)
- `name1: str` — First party name
- `name2: str` — Second party name

**Output:** `dict` with keys:
- `df` — pandas DataFrame of the survey data
- `meta` — pyreadstat metadata object
- `sav_labels` — `list[tuple[str, str]]` of `(column_name, label)` pairs
- `name1`, `name2` — the party names passed in

**Example 1 — Streamlit uploaded file:**
```python
result = SPSSMatchProcessor.get_essentials_from_sav(uploaded_file, "Plaintiff", "Defense")
sav_labels = result['sav_labels']
# [("Q1", "How old are you?"), ("Q32", "Do you believe the defendant..."), ...]
```

**Example 2 — Local file path:**
```python
result = SPSSMatchProcessor.get_essentials_from_sav("/data/cerrito_survey.sav", "Wine Warehouse", "Golden State Cider")
result['df'].shape       # (250, 48) — 250 jurors, 48 columns
result['name1']          # "Wine Warehouse"
```

---

### `_build_label_mapping()` *(abstract)*

Converts `sav_labels` into a reverse lookup dict.

**Output:** `dict[str, str]` mapping label text → column name.

**Example 1:**
```python
# Given sav_labels = [("Q1", "How old are you?"), ("Q32", "Did Bob eat the cookie?")]
# Returns: {"How old are you?": "Q1", "Did Bob eat the cookie?": "Q32"}
```

**Example 2:**
```python
# Given sav_labels = [("PlaaffsQ1", "Was the defendant negligent?"), ("DefaffsQ1", "Did the plaintiff contribute?")]
# Returns: {"Was the defendant negligent?": "PlaaffsQ1", "Did the plaintiff contribute?": "DefaffsQ1"}
```

---

### `_normalize_text(text)` *(abstract)*

Normalizes whitespace and hyphens for fuzzy matching.

**Input:** Raw string, e.g. `"Do you  think   Bob  ate -  the cookie?"`

**Output:** Cleaned string, e.g. `"Do you think Bob ate-the cookie?"`

**Example 1:**
```python
_normalize_text("Do you  think   Bob  ate -  the cookie?")
# Returns: "Do you think Bob ate-the cookie?"
```

**Example 2:**
```python
_normalize_text("Was the defendant  - negligent  -  or not?")
# Returns: "Was the defendant-negligent-or not?"
```

---

### `_find_column(question)` *(abstract)*

Looks up the SAV column name for a given question. Tries exact match first, then partial match using normalized text.

**Input:** `question: str` — The question text to search for

**Output:** Column name string (e.g. `"Q32"`) if found, `None` if not found

**Example 1 — exact match:**
```python
column = processor._find_column("Do you think the defendant was negligent?")
# Label exists verbatim in the SAV → Returns "Q14"
```

**Example 2 — partial match:**
```python
column = processor._find_column("defendant was negligent")
# Shorter string found inside a longer label → Returns "Q14"
# Returns None if no label contains this substring
```

---

### `get_all_general_questions(name1, name2)` *(abstract)*

Returns all survey questions that appear before the party-specific questions begin. Filters out metadata fields (name, email, address) and text-input fields.

**Input:**
- `name1: str` — Default `"Plaaffs"` (prefix used in column names for party-specific questions)
- `name2: str` — Default `"Defaffs"`

**Output:** `list[tuple[str, str]]` of `(column_name, label)` for general questions only

**Example 1:**
```python
general = processor.get_all_general_questions("Plaaffs", "Defaffs")
# [("Q1", "How old are you?"), ("Q2", "What is your occupation?"), ...]
# Stops before hitting columns like "PlaaffsQ1", "DefaffsQ1"
```

**Example 2 — metadata filtered out:**
```python
# SAV columns: ["firstname", "Q1", "Q2", "email", "Q3", "PlaaffsQ1"]
general = processor.get_all_general_questions("Plaaffs", "Defaffs")
# "firstname" and "email" skipped; stops at "PlaaffsQ1"
# Returns [("Q1", "How old are you?"), ("Q2", "What is your gender?"), ("Q3", "What is your occupation?")]
```

---

### `get_matched_questions()`

Returns a copy of all questions that were successfully matched during processing.

**Output:** `list[tuple[str, str]]`

**Example 1:**
```python
processor.get_matched_questions()
# [("Plaintiff", "Was the defendant negligent?"), ("Plaintiff", "Did the product fail?")]
```

**Example 2:**
```python
# After a run with no matches
processor.get_matched_questions()
# []
```

---

### `get_unmatched_questions()`

Returns a copy of all questions that failed to match.

**Output:** `list[tuple[str, str]]`

**Example 1:**
```python
processor.get_unmatched_questions()
# [("Defense", "Did the plaintiff misuse the product?")]
```

**Example 2:**
```python
# Useful for debugging label mismatches
for category, question in processor.get_unmatched_questions():
    print(f"[{category}] Could not find: {question}")
# [Defense] Could not find: Did the plaintiff misuse the product?
```

---

### `get_result()`

Returns both matched and unmatched lists as a named tuple.

**Output:** `SPSSResult(matched=[...], unmatched=[...])`

**Example 1:**
```python
result = processor.get_result()
result.matched    # [("Plaintiff", "Was the defendant negligent?")]
result.unmatched  # [("Defense", "Did the plaintiff misuse the product?")]
```

**Example 2:**
```python
# Useful for structured logging
result = processor.get_result()
print(f"{len(result.matched)} matched, {len(result.unmatched)} unmatched")
# "3 matched, 1 unmatched"
```

---

### `reset_tracking()`

Clears `_matched` and `_unmatched` lists. Called automatically at the start of each new processing run.

**Example 1:**
```python
processor.reset_tracking()
processor.get_matched_questions()  # []
processor.get_unmatched_questions()  # []
```

**Example 2:**
```python
# Run once, inspect, then reset and run again with new questions
result1 = processor.find_all_matches(old_questions, [])
processor.reset_tracking()
result2 = processor.find_all_matches(new_questions, [])
```

---

## `spss_match_processor.py` — `SPSSMatchProcessor`

Concrete implementation of `SPSSProcessor`. Provides the actual matching logic and SAV file reading.

---

### `_build_label_mapping()`

Builds a `{label: column}` dict from `self._sav_labels`.

**Example 1:**
```python
# Given sav_labels = [("Q1", "How old are you?"), ("Q32", "Did Bob eat the cookie?")]
# Returns: {"How old are you?": "Q1", "Did Bob eat the cookie?": "Q32"}
```

**Example 2:**
```python
# Given sav_labels = [("PlaaffsQ1", "Was the defendant negligent?"), ("DefaffsQ1", "Did the plaintiff contribute?")]
# Returns: {"Was the defendant negligent?": "PlaaffsQ1", "Did the plaintiff contribute?": "DefaffsQ1"}
```

---

### `_normalize_text(text)`

Collapses multiple spaces to one and removes spaces around hyphens.

**Example 1:**
```python
_normalize_text("Is  the defendant  - liable?")
# Returns: "Is the defendant-liable?"
```

**Example 2:**
```python
_normalize_text("Did  the  plaintiff   suffer  harm  -   based on negligence?")
# Returns: "Did the plaintiff suffer harm-based on negligence?"
```

---

### `_find_column(question)`

Searches for a matching column using exact match, then partial/substring match with normalization.

**Input:** `question: str`

**Output:** Column name `str` or `None`

**Example 1 — partial match:**
```python
_find_column("Was the defendant negligent")
# Exact match fails, but finds it as a substring of "Q14"'s label
# Returns "Q14"
```

**Example 2 — no match:**
```python
_find_column("Did the jury like pizza")
# Neither exact nor partial match found
# Returns None
```

---

### `find_all_matches(name1_questions, name2_questions)`

Main entry point for batch matching. Processes all questions for both parties and tracks results.

**Input:**
- `name1_questions: list[str]` — Question texts for party 1
- `name2_questions: list[str]` — Question texts for party 2

**Output:** `SPSSResult(matched=[...], unmatched=[...])`

**Example 1 — mixed results:**
```python
result = processor.find_all_matches(
    name1_questions=["Was the defendant negligent?", "Did the product fail?"],
    name2_questions=["Did the plaintiff misuse the product?"]
)
# result.matched = [("Plaintiff", "Was the defendant negligent?"), ...]
# result.unmatched = [("Defense", "Did the plaintiff misuse the product?")]  # if not found
```

**Example 2 — checking counts:**
```python
result = processor.find_all_matches(
    name1_questions=["Was Performance Food Group negligent?"],
    name2_questions=["Was Cerrito partially at fault?", "Did Cerrito ignore safety warnings?"]
)
len(result.matched)    # 2  — two questions found in SAV
len(result.unmatched)  # 1  — one question text didn't match any label
```

---

### `get_all_general_questions(name1, name2)`

Returns all general (non-party-specific) survey questions before party columns begin, filtering out metadata and free-text fields.

**Input:** `name1: str`, `name2: str` — Column name prefixes that signal the start of party-specific questions

**Excludes columns where:**
- Column name is in the metadata set (`firstname`, `lastname`, `email`, etc.)
- Label contains text input patterns (`"please enter"`, `"first name"`, `"address"`, etc.)
- Column name contains `name1` or `name2` (stops iteration at first match)

**Output:** `list[tuple[str, str]]`

**Example 1:**
```python
general = processor.get_all_general_questions("Plaaffs", "Defaffs")
# Returns questions like age, occupation, pre-existing opinions
# Stops when it hits a column named "PlaaffsQ1"
```

**Example 2 — metadata filtered out:**
```python
# SAV has columns: ["firstname", "Q1", "Q2", "email", "Q3", "PlaaffsQ1"]
general = processor.get_all_general_questions("Plaaffs", "Defaffs")
# "firstname" and "email" are excluded as metadata columns
# Returns [("Q1", "How old are you?"), ("Q2", "What is your occupation?"), ("Q3", "How familiar are you with this case?")]
# "PlaaffsQ1" triggers the break — nothing after it is included
```

---

### `get_essentials_from_sav(sav_file, name1, name2)` *(static)*

Reads a SAV file using `pyreadstat`. Handles both file paths and Streamlit `UploadedFile` objects by writing to a temp file.

**Input:**
- `sav_file` — File path string or uploaded file object
- `name1: str`, `name2: str` — Party names

**Output:** `dict` with `df`, `meta`, `sav_labels`, `name1`, `name2`

**Example 1 — Streamlit integration:**
```python
essentials = SPSSMatchProcessor.get_essentials_from_sav(st.file_uploader(...), "Plaintiff", "Defense")
processor = SPSSSyntaxGenerator(essentials['sav_labels'], essentials['name1'], essentials['name2'])
```

**Example 2 — inspecting the output:**
```python
essentials = SPSSMatchProcessor.get_essentials_from_sav("mock_trial_survey.sav", "Wine Warehouse", "Golden State Cider")
print(len(essentials['sav_labels']))   # 52 — number of columns in the SAV
print(essentials['sav_labels'][:2])    # [("Q1", "How old are you?"), ("Q2", "What is your gender?")]
```

---

## `spss_syntax.py` — `SPSSSyntaxGenerator`

Extends `SPSSMatchProcessor` with SPSS recode syntax generation.

---

### `RecodeResult` (NamedTuple)

| Field | Type | Description |
|-------|------|-------------|
| `script` | `str` | The full generated SPSS syntax |
| `matched` | `list[tuple[str, str]]` | Successfully matched questions |
| `unmatched` | `list[tuple[str, str]]` | Questions with no SAV match |

---

### `__init__(sav_labels, name1, name2)`

Initializes generator with an empty `_script` string and calls `super().__init__()`.

**Default party names:** `"Plaintiff"` / `"Defense"`

---

### `generate_recode_script(name1_questions, name2_questions, recode_settings)`

Main entry point. Generates a full SPSS recode script for all questions across both parties plus any neutral questions found in `recode_settings`.

**Input:**
- `name1_questions: list[str]` — Question texts for party 1
- `name2_questions: list[str]` — Question texts for party 2
- `recode_settings: dict[str, dict[str, int]]` — Per-question configuration dict. Keys are question texts, values are dicts with recode parameters (see `_generate_recode_syntax` for fields). Neutral questions are identified by `settings.get('party') == 'neutral'`.

**Output:** `RecodeResult(script=..., matched=..., unmatched=...)`

**Example 1 — categorical variable:**
```python
result = generator.generate_recode_script(
    name1_questions=["Was the defendant negligent?"],
    name2_questions=["Did the plaintiff contribute?"],
    recode_settings={
        "Was the defendant negligent?": {
            "variable_type": "categorical",
            "range1_start": 1, "range1_end": 3, "range1_becomes": 1,
            "range2_start": 4, "range2_end": 7, "range2_becomes": 2
        }
    }
)
print(result.script)
# recode Q14 (1 thru 3=1) (4 thru 7=2) into Q14.r.
# variable labels Q14.r 'Was the defendant negligent?'.
# value labels Q14.r 1 'Plaintiff' 2 'Defense'.
# execute.
```

**Example 2 — continuous variable with neutral question:**
```python
result = generator.generate_recode_script(
    name1_questions=[],
    name2_questions=[],
    recode_settings={
        "Overall case strength rating": {
            "variable_type": "continuous",
            "party": "neutral",
            "matched_column": "Q5",
            "range1_operator": "<", "range1_value": 5, "range1_becomes": 1,
            "range2_operator": ">=", "range2_value": 5, "range2_becomes": 2
        }
    }
)
print(result.script)
# recode Q5 (LOWEST thru 4.99=1) (5 thru HIGHEST=2) into Q5.r.
# variable labels Q5.r 'Overall case strength rating'.
# value labels Q5.r 1 'Plaintiff' 2 'Defense'.
# execute.
```

---

### `_process_questions(questions, category, recode_settings)`

Internal helper. Iterates a list of questions, finds their columns, generates syntax for each, and updates `_matched`/`_unmatched`.

For neutral questions, uses `recode_settings[question]['matched_column']` directly instead of searching.

**Input:**
- `questions: list[str]`
- `category: str` — e.g. `"Plaintiff"`, `"Defense"`, or `"Neutral"`
- `recode_settings: dict[str, dict]`

---

### `_generate_recode_syntax(column, question, settings)`

Generates the SPSS syntax block for a single question. Supports two variable types:

**Categorical** (default): Uses `thru` ranges.
```
recode Q14 (1 thru 3=1) (4 thru 7=2) into Q14.r.
variable labels Q14.r 'Was the defendant negligent?'.
value labels Q14.r 1 'Plaintiff' 2 'Defense'.
execute.
```

Required keys in `settings`: `range1_start`, `range1_end`, `range1_becomes`, `range2_start`, `range2_end`, `range2_becomes`

**Continuous**: Uses operator-based ranges via `_operator_to_spss_range`.
```
recode Q22 (LOWEST thru 3.99=1) (4 thru HIGHEST=2) into Q22.r.
```

Required keys: `range1_operator`, `range1_value`, `range1_becomes`, `range2_operator`, `range2_value`, `range2_becomes`

---

### `_operator_to_spss_range(operator, value)`

Converts a Python comparison operator and threshold into SPSS range syntax.

| Operator | Input | Output |
|----------|-------|--------|
| `<` | `4` | `LOWEST thru 3.99` |
| `<=` | `4` | `LOWEST thru 4` |
| `=` | `4` | `4` |
| `>=` | `4` | `4 thru HIGHEST` |
| `>` | `4` | `4.01 thru HIGHEST` |

**Example 1:**
```python
_operator_to_spss_range("<=", 5)
# Returns "LOWEST thru 5"

_operator_to_spss_range(">", 3)
# Returns "3.01 thru HIGHEST"
```

**Example 2:**
```python
_operator_to_spss_range("<", 4)
# Returns "LOWEST thru 3.99"

_operator_to_spss_range("=", 7)
# Returns "7"
```

---

### `get_script()`

Returns the full generated SPSS script string from the last `generate_recode_script` call.

**Output:** `str`

**Example 1:**
```python
generator.generate_recode_script(...)
print(generator.get_script())
# recode Q14 (1 thru 3=1) (4 thru 7=2) into Q14.r.
# variable labels Q14.r 'Was the defendant negligent?'.
# value labels Q14.r 1 'Plaintiff' 2 'Defense'.
# execute.
```

**Example 2 — write to file:**
```python
with open("recode_script.sps", "w") as f:
    f.write(generator.get_script())
```
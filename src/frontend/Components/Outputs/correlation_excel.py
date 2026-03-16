"""
Applies recode settings to a SAV dataframe and generates a correlation table as a downloadable Excel file.
Meant to be called after render_sav_processor() in main.py.
"""
import io
import pandas as pd
import streamlit as st


def _convert_value(value, settings: dict):
    """
    Apply recode logic to a single value based on its settings.

    Args:
        value: Raw survey response value
        settings: The recode config dict for this question from recode_settings

    Returns:
        Recoded integer (1 or 2), or None if value doesn't match any range
    """
    if pd.isna(value):
        return None

    variable_type = settings.get('variable_type', 'categorical')

    if variable_type == 'continuous':
        # Evaluate range1
        op1 = settings['range1_operator']
        val1 = settings['range1_value']
        becomes1 = settings['range1_becomes']

        if   op1 == '<'  and value <  val1: return becomes1
        elif op1 == '<=' and value <= val1: return becomes1
        elif op1 == '='  and value == val1: return becomes1
        elif op1 == '>=' and value >= val1: return becomes1
        elif op1 == '>'  and value >  val1: return becomes1

        # Evaluate range2
        op2 = settings['range2_operator']
        val2 = settings['range2_value']
        becomes2 = settings['range2_becomes']

        if   op2 == '<'  and value <  val2: return becomes2
        elif op2 == '<=' and value <= val2: return becomes2
        elif op2 == '='  and value == val2: return becomes2
        elif op2 == '>=' and value >= val2: return becomes2
        elif op2 == '>'  and value >  val2: return becomes2

        return None

    else:
        # Categorical — thru ranges
        if settings['range1_start'] <= value <= settings['range1_end']:
            return settings['range1_becomes']
        elif settings['range2_start'] <= value <= settings['range2_end']:
            return settings['range2_becomes']
        return None


def apply_recodes(df: pd.DataFrame, recode_settings: dict) -> pd.DataFrame:
    """
    Apply all recode settings to the dataframe, adding .r columns.

    Args:
        df: Raw SAV dataframe from sav_data['df']
        recode_settings: st.session_state.recode_settings

    Returns:
        Copy of df with new .r columns appended
    """
    df = df.copy()

    for label, settings in recode_settings.items():
        column = settings.get('column') or settings.get('matched_column')
        if not column or column not in df.columns:
            continue

        df[f"Recode: {label}"] = df[column].apply(lambda x: _convert_value(x, settings))

    return df


def build_correlation_table(df: pd.DataFrame, recode_settings: dict) -> pd.DataFrame:
    """
    Build a correlation matrix from all recoded label columns, deduplicating first.

    Args:
        df: Dataframe with recoded label columns already applied
        recode_settings: Used to identify which columns are recoded labels

    Returns:
        Correlation matrix as a DataFrame
    """
    # Get label columns in order, deduplicating
    label_cols = list(dict.fromkeys([
    f"Recode: {label}" for label in recode_settings.keys()
    if f"Recode: {label}" in df.columns
]))

    if not label_cols:
        return pd.DataFrame()

    return df[label_cols].corr().abs()


def _write_styled_excel(corr_matrix: pd.DataFrame) -> io.BytesIO:
    """
    Write correlation matrix to a styled Excel buffer matching SPSS style:
    - Blue font throughout
    - Alternating gray row shading
    - Bold header row and index column

    Args:
        corr_matrix: Correlation matrix DataFrame

    Returns:
        BytesIO buffer ready for st.download_button
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    BLUE_FONT   = Font(color="1F3864", bold=False)
    BLUE_BOLD   = Font(color="1F3864", bold=True)
    GRAY_FILL   = PatternFill("solid", fgColor="D9D9D9")
    WHITE_FILL  = PatternFill("solid", fgColor="FFFFFF")
    HEADER_FILL = PatternFill("solid", fgColor="BDD7EE")  # light blue header like SPSS
    THIN_BORDER = Border(
        bottom=Side(style="thin", color="BFBFBF"),
        right=Side(style="thin", color="BFBFBF")
    )
    WRAP = Alignment(wrap_text=True, vertical="center", horizontal="center")
    WRAP_LEFT = Alignment(wrap_text=True, vertical="center", horizontal="left")

    wb = Workbook()
    ws = wb.active
    ws.title = "Correlation Table"

    labels = list(corr_matrix.columns)
    n = len(labels)

    # Row 1: column headers (offset by 1 for the index column)
    ws.cell(row=1, column=1, value="")  # top-left corner blank
    for col_idx, label in enumerate(labels, start=2):
        cell = ws.cell(row=1, column=col_idx, value=label)
        cell.font = BLUE_BOLD
        cell.fill = HEADER_FILL
        cell.alignment = WRAP
        cell.border = THIN_BORDER

    # Data rows
    for row_idx, label in enumerate(labels, start=2):
        is_gray = (row_idx % 2 == 0)
        row_fill = GRAY_FILL if is_gray else WHITE_FILL

        # Index cell (row label)
        idx_cell = ws.cell(row=row_idx, column=1, value=label)
        idx_cell.font = BLUE_BOLD
        idx_cell.fill = HEADER_FILL
        idx_cell.alignment = WRAP_LEFT
        idx_cell.border = THIN_BORDER

        # Correlation values
        for col_idx, col_label in enumerate(labels, start=2):
            val = corr_matrix.loc[label, col_label]
            cell = ws.cell(row=row_idx, column=col_idx, value=round(val, 3))
            cell.font = BLUE_FONT
            cell.fill = row_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = THIN_BORDER

    # Column widths — index col wider for label text, data cols narrow
    ws.column_dimensions["A"].width = 35
    for col_idx in range(2, n + 2):
        ws.column_dimensions[get_column_letter(col_idx)].width = 18

    # Row heights
    ws.row_dimensions[1].height = 120  # header row taller for wrapped labels
    for row_idx in range(2, n + 2):
        ws.row_dimensions[row_idx].height = 120

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def render_correlation_exporter():
    """
    Streamlit component that applies recodes, builds correlation table,
    and renders a download button for the Excel file.

    Drop this right after render_sav_processor() in main.py.
    """
    sav_data = st.session_state.get('sav_data')
    recode_settings = st.session_state.get('recode_settings')

    if not sav_data or not recode_settings:
        return

    df = sav_data['df']

    try:
        recoded_df = apply_recodes(df, recode_settings)
        corr_matrix = build_correlation_table(recoded_df, recode_settings)

        if corr_matrix.empty:
            st.warning("⚠️ No recoded columns found to correlate.")
            return

        # Write styled Excel to in-memory buffer
        buffer = _write_styled_excel(corr_matrix)

        st.subheader("📈 Correlation Table")
        st.download_button(
            label="📥 Download Correlation Table (.xlsx)",
            data=buffer,
            file_name="correlation_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

    except Exception as e:
        st.error(f"❌ Error generating correlation table: {str(e)}")
        st.exception(e)
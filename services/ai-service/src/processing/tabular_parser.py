"""
Tabular parser: extract text from CSV and XLSX files.
"""

from pathlib import Path


def extract_text_from_csv(path: str) -> str:
    """
    Extract text from a CSV file. Returns table as plain text (rows joined).
    """
    import pandas as pd

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    try:
        df = pd.read_csv(path)
        return df.to_string(index=False)
    except Exception as e:
        raise ValueError(f"Could not read CSV {path}: {e}") from e


def extract_text_from_xlsx(path: str) -> str:
    """
    Extract text from an XLSX file. Reads first sheet; returns table as plain text.
    """
    import pandas as pd

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"XLSX file not found: {path}")
    try:
        df = pd.read_excel(path, sheet_name=0)
        return df.to_string(index=False)
    except Exception as e:
        raise ValueError(f"Could not read XLSX {path}: {e}") from e


def extract_text_from_tabular(path: str) -> str:
    """
    Dispatch by extension: .csv -> extract_text_from_csv, .xlsx/.xls -> extract_text_from_xlsx.
    """
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return extract_text_from_csv(path)
    if suffix in (".xlsx", ".xls"):
        return extract_text_from_xlsx(path)
    raise ValueError(f"Unsupported tabular extension: {suffix}")

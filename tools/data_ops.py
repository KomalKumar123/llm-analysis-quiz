import io
import pandas as pd
import pdfplumber


def compute_from_csv(file_bytes: bytes, operation: str = "sum", column: str = "value"):
    df = pd.read_csv(io.BytesIO(file_bytes))

    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in CSV")

    series = df[column]

    if operation == "sum":
        return float(series.sum())
    elif operation == "mean":
        return float(series.mean())
    elif operation == "max":
        return float(series.max())
    elif operation == "min":
        return float(series.min())
    else:
        raise ValueError(f"Unsupported operation: {operation}")


def compute_from_pdf(file_bytes: bytes, page_no: int = 0, column_index: int = 0):
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page = pdf.pages[page_no]
        table = page.extract_table()

        if not table:
            raise ValueError("No table found in PDF")

        values = []
        # Skip header row
        for row in table[1:]:
            try:
                values.append(float(row[column_index]))
            except Exception:
                # Ignore non-numeric cells
                pass

        return float(sum(values))

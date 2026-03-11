import pandas as pd
import os

def safe_load_csv(file):
    """
    Safely loads a CSV file by trying multiple encodings.
    """
    encodings = ["utf-8", "latin1", "ISO-8859-1"]
    df = pd.DataFrame()

    for enc in encodings:
        try:
            df = pd.read_csv(file, encoding=enc)
            if enc != "utf-8":
                print(f"Warning: fallback encoding used ({enc})")
            break
        except Exception:
            if hasattr(file, 'seek'):
                file.seek(0)
            continue

    if not df.empty:
        # Non-destructive light column sanitization 
        df.columns = (
            df.columns
              .astype(str)
              .str.replace(r"[^\x20-\x7E]", "", regex=True)
              .str.strip()
        )

    return df

def load_dataset(file_path=None):
    """
    Load dataset from file path or fallback to default location.
    """
    if file_path is None:
        file_path = "data/Nykaa Digital Marketing.csv"

    if not os.path.exists(file_path):
        return pd.DataFrame()

    with open(file_path, "rb") as f:
        return safe_load_csv(f)
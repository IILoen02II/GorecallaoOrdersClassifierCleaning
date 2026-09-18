import unicodedata
import pandas as pd

def _normalize_column(col: str) -> str:
    """Normalize a column name to lowercase for consistent access."""
    return col.lower()

def clear_script(route_csv: str) -> pd.DataFrame:

    # 1. Load raw data
    df = pd.read_csv(route_csv, sep=",", encoding="cp850")

    # 2. Normalize column names (e.g. "Fecha_Orden" -> "fecha_orden")
    df.columns = [_normalize_column(col) for col in df.columns]

    # 3. Trim whitespace from all text columns
    col_tex = df.select_dtypes(include="object").columns
    for col in col_tex:
        df[col] = df[col].str.strip()

    # 4. Parse the order date and drop the (always empty) time component
    # Previously inspected using the `header` parameter: the time portion of
    # "fecha_orden" was always 00:00:00, so it was unnecessary and is
    # dropped here, keeping only the date.
    df["fecha_orden"] = pd.to_datetime(df["fecha_orden"],format="%d/%m/%Y %H:%M:%S", errors="coerce")
    df["fecha_orden"] = df["fecha_orden"].dt.date

    # 5. Ensure the RUC (tax ID) column is treated as text, not a number
    ruc = df["nro_ruc"] = df["nro_ruc"].astype(str)

    # 6. Standardize casing for key categorical text fields
    for col in ["fase_orden", "tipo_bien"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()

    # 7. Convert low-cardinality columns to 'category' dtype
    for col in ["fase_orden", "tipo_bien", "tipo_proceso"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # 8. Replace placeholder values with proper missing values (NA)
    corrections = {
        "." : pd.NA, 
        "0" : pd.NA
    }

    df["nro_proc_sel"] = df["nro_proc_sel"].replace(corrections)

     # 9. Flag rows with an invalid negative amount
    # A negative "total_fact_moneda" (total invoiced amount) is only
    # expected for orders in the "Rebaja" (discount) or "Anulado" (voided)
    # phase; any other negative value is considered invalid data.
    invalid = ((df["total_fact_moneda"] < 0) & (~df["fase_orden"].isin(["Rebaja", "Anulado"])))

    return df
import unicodedata
import pandas as pd

def _normalize_column(col: str) -> str:
    return col.lower()

def clear_script(route_csv: str) -> pd.DataFrame:

    df = pd.read_csv(route_csv, sep=",", encoding="cp850")

    df.columns = [_normalize_column(col) for col in df.columns]

    col_tex = df.select_dtypes(include="object").columns
    for col in col_tex:
        df[col] = df[col].str.strip()
   

    df["fecha_orden"] = pd.to_datetime(df["fecha_orden"],format="%d/%m/%Y %H:%M:%S", errors="coerce")
    df["fecha_orden"] = df["fecha_orden"].dt.date

    ruc = df["nro_ruc"] = df["nro_ruc"].astype(str)

    for col in ["fase_orden", "tipo_bien"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()

    for col in ["fase_orden", "tipo_bien", "tipo_proceso"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    corrections = {
        "." : pd.NA, 
        "0" : pd.NA
    }

    df["nro_proc_sel"] = df["nro_proc_sel"].replace(corrections)

    invalid = ((df["total_fact_moneda"] < 0) & (~df["fase_orden"].isin(["Rebaja", "Anulado"])))

    return df
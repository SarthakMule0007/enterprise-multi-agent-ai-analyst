import pandas as pd


def analyze_rows(rows: list[dict]) -> dict:
    if not rows:
        return {"row_count": 0, "summary": "The query returned no rows.", "numeric": {}}
    frame = pd.DataFrame(rows)
    numeric = {}
    for col in frame.columns:
        # SQL NUMERIC values arrive from psycopg as Decimal/object values.
        series = pd.to_numeric(frame[col], errors="coerce").dropna()
        if series.empty:
            continue
        if not series.empty:
            numeric[col] = {"sum": float(series.sum()), "mean": float(series.mean()),
                            "min": float(series.min()), "max": float(series.max())}
    summary = f"Returned {len(rows)} rows across {len(frame.columns)} columns."
    return {"row_count": len(rows), "summary": summary, "numeric": numeric}

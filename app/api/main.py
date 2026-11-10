from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.analytics.database import describe_schema, get_engine
from app.analytics.graph import analyze

app = FastAPI(title="Enterprise Multi-Agent AI Analyst", version="0.1.0",
              description="Natural language analytics with a supervised SQL and reporting workflow.")


class AnalyzeRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


@app.get("/health")
def health():
    try:
        with get_engine().connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")


@app.get("/schema")
def schema():
    try:
        return {"tables": describe_schema()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.post("/analyze")
def analyze_question(body: AnalyzeRequest):
    try:
        result = analyze(body.question)
        return {"question": body.question, **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

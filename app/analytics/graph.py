from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from app.analytics.database import run_readonly_query
from app.analytics.sql_agent import plan_sql
from app.analytics.stats_agent import analyze_rows
from app.retrieval.rag import retrieve


class AnalysisState(TypedDict, total=False):
    question: str
    sql: str
    rows: list[dict]
    stats: dict
    context: list[str]
    report: str
    error: str


def sql_worker(state: AnalysisState) -> dict:
    try:
        sql = plan_sql(state["question"])
        rows = run_readonly_query(sql)
        return {"sql": sql, "rows": rows}
    except Exception as exc:
        return {"error": str(exc), "rows": [], "sql": ""}


def stats_worker(state: AnalysisState) -> dict:
    return {"stats": analyze_rows(state.get("rows", []))}


def rag_worker(state: AnalysisState) -> dict:
    return {"context": retrieve(state["question"])}


def report_worker(state: AnalysisState) -> dict:
    settings_msg = ""
    if state.get("error"):
        return {"report": f"I could not complete this analysis: {state['error']}"}
    rows, stats, context = state.get("rows", []), state.get("stats", {}), state.get("context", [])
    try:
        from app.config import get_settings
        cfg = get_settings()
        if cfg.use_llm:
            from langchain_openai import ChatOpenAI
            prompt = f"Answer the user's business question using only the supplied evidence. State uncertainty and cite relevant definitions.\nQuestion: {state['question']}\nStatistics: {stats}\nRows (sample): {rows[:20]}\nDefinitions: {context}"
            report = ChatOpenAI(model=cfg.llm_model, temperature=0).invoke(prompt).content
            return {"report": report}
    except Exception as exc:
        settings_msg = f" (Model unavailable; deterministic report shown: {exc})"
    facts = [f"**{col}**: total {v['sum']:,.2f}, average {v['mean']:,.2f}, range {v['min']:,.2f}–{v['max']:,.2f}." for col, v in stats.get("numeric", {}).items()]
    report = f"Analysis of: {state['question']}\n\n{stats.get('summary', '')} " + " ".join(facts)
    if context:
        report += "\n\nMetric context:\n" + "\n".join(f"- {item}" for item in context)
    if settings_msg:
        report += settings_msg
    return {"report": report}


def build_graph():
    graph = StateGraph(AnalysisState)
    graph.add_node("sql_worker", sql_worker)
    graph.add_node("stats_worker", stats_worker)
    graph.add_node("rag_worker", rag_worker)
    graph.add_node("report_worker", report_worker)
    graph.add_edge(START, "sql_worker")
    graph.add_edge("sql_worker", "stats_worker")
    graph.add_edge("stats_worker", "rag_worker")
    graph.add_edge("rag_worker", "report_worker")
    graph.add_edge("report_worker", END)
    return graph.compile()


def analyze(question: str) -> dict[str, Any]:
    if not question.strip():
        raise ValueError("Question cannot be empty.")
    return build_graph().invoke({"question": question.strip()})

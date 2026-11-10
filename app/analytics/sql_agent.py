from app.analytics.database import describe_schema


def demo_sql(question: str) -> str:
    q = question.lower()
    from app.analytics.database import get_engine
    is_sqlite = get_engine().dialect.name == "sqlite"
    if any(w in q for w in ("region", "geography", "area")):
        return "SELECT region, COUNT(*) AS order_count, SUM(revenue) AS revenue FROM orders GROUP BY region ORDER BY revenue DESC"
    if any(w in q for w in ("product", "category", "item")):
        return "SELECT product_category, COUNT(*) AS order_count, SUM(revenue) AS revenue FROM orders GROUP BY product_category ORDER BY revenue DESC"
    if any(w in q for w in ("month", "monthly", "trend", "change", "over time")):
        if is_sqlite:
            return "SELECT strftime('%Y-%m-01', order_date) AS month, SUM(revenue) AS revenue, COUNT(*) AS order_count FROM orders GROUP BY 1 ORDER BY 1"
        return "SELECT DATE_TRUNC('month', order_date)::date AS month, SUM(revenue) AS revenue, COUNT(*) AS order_count FROM orders GROUP BY 1 ORDER BY 1"
    if any(w in q for w in ("average", "avg", "mean", "typical")):
        return "SELECT product_category, AVG(revenue) AS average_order_revenue, COUNT(*) AS order_count FROM orders GROUP BY product_category ORDER BY average_order_revenue DESC"
    return "SELECT region, COUNT(*) AS order_count, SUM(revenue) AS revenue FROM orders GROUP BY region ORDER BY revenue DESC"


def plan_sql(question: str) -> str:
    from app.config import get_settings
    settings = get_settings()
    if not settings.use_llm:
        return demo_sql(question)
    from langchain_openai import ChatOpenAI
    schema = describe_schema()
    prompt = f"""Write exactly one PostgreSQL SELECT statement answering the question. Never modify data.
Available schema: {schema}
Question: {question}
Return SQL only. Use only listed tables/columns."""
    response = ChatOpenAI(model=settings.llm_model, temperature=0).invoke(prompt)
    return response.content.strip().removeprefix("```sql").removesuffix("```").strip()

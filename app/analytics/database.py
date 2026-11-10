from functools import lru_cache
from sqlalchemy import create_engine, inspect, text
from app.config import get_settings


@lru_cache
def get_engine():
    url = get_settings().database_url
    options = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, connect_args=options)


def describe_schema() -> dict:
    inspector = inspect(get_engine())
    return {table: [col["name"] for col in inspector.get_columns(table)]
            for table in inspector.get_table_names()}


def run_readonly_query(sql: str, limit: int = 500) -> list[dict]:
    normalized = sql.strip().rstrip(";").strip()
    lowered = normalized.lower()
    if not lowered.startswith("select ") and not lowered.startswith("with "):
        raise ValueError("Only SELECT queries are allowed.")
    forbidden = (";", "--", "/*", "*/", " insert ", " update ", " delete ",
                 " drop ", " alter ", " create ", " truncate ", " grant ", " revoke ")
    padded = f" {lowered} "
    if any(token in padded for token in forbidden):
        raise ValueError("Query contains a disallowed token or multiple statements.")
    engine = get_engine()
    with engine.connect() as conn:
        with conn.begin():
            if engine.dialect.name == "sqlite":
                conn.exec_driver_sql("PRAGMA query_only = ON")
            elif engine.dialect.name == "postgresql":
                conn.exec_driver_sql("SET TRANSACTION READ ONLY")
                conn.exec_driver_sql("SET LOCAL statement_timeout = '10s'")
            result = conn.execute(text(f"SELECT * FROM ({normalized}) AS analyst_result LIMIT {int(limit)}"))
            return [dict(row._mapping) for row in result]

"""MCP tools for analyst clients. Run with: python -m app.mcp_server.server"""
from mcp.server.fastmcp import FastMCP
from app.analytics.database import describe_schema
from app.analytics.graph import analyze

mcp = FastMCP("Enterprise AI Analyst")


@mcp.tool()
def get_schema() -> dict:
    """List accessible database tables and columns."""
    return describe_schema()


@mcp.tool()
def analyze_question(question: str) -> dict:
    """Analyze a business question and return report, SQL, statistics, and evidence."""
    return analyze(question)


if __name__ == "__main__":
    mcp.run()

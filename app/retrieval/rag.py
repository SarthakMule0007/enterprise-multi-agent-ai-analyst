from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[2]


def retrieve(question: str, k: int = 3) -> list[str]:
    docs = []
    for path in (ROOT / "data" / "knowledge").glob("*.md"):
        docs.extend(p.strip() for p in path.read_text(encoding="utf-8").split("\n\n") if p.strip())
    if not docs:
        return []
    matrix = TfidfVectorizer(stop_words="english").fit_transform([question, *docs])
    scores = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
    indices = scores.argsort()[::-1][:k]
    return [docs[i] for i in indices if scores[i] > 0]

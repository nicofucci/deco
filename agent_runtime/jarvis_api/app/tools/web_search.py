from typing import List, Dict

try:
    from duckduckgo_search import DDGS
except Exception as e:  # pragma: no cover - fallback when lib missing
    DDGS = None
    _import_error = e


def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    Simple wrapper around duckduckgo-search to avoid leaking provider details.
    Returns a list of dicts with title, link and snippet.
    """
    if DDGS is None:
        return [{"title": "web_search_unavailable", "link": "", "snippet": f"Error importando duckduckgo-search: {_import_error}"}]

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            parsed = []
            for item in results:
                parsed.append(
                    {
                        "title": item.get("title"),
                        "link": item.get("href") or item.get("link"),
                        "snippet": item.get("body") or item.get("snippet"),
                    }
                )
            return parsed
    except Exception as exc:  # pragma: no cover - network errors
        return [{"title": "web_search_error", "link": "", "snippet": str(exc)}]

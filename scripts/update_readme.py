#!/usr/bin/env python3

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path


README_PATH = Path(__file__).resolve().parents[1] / "README.md"
ZENN_USERNAME = "nenene01"
ARTICLE_COUNT = 5


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Nenene01-profile-readme"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def escape_markdown(text: str) -> str:
    normalized = " ".join(text.split())
    return re.sub(r"([\\\[\]<>])", r"\\\1", normalized)


def latest_zenn_articles() -> list[str]:
    query = urllib.parse.urlencode(
        {
            "username": ZENN_USERNAME,
            "count": ARTICLE_COUNT,
            "order": "latest",
        }
    )
    data = fetch_json(f"https://zenn.dev/api/articles?{query}")

    articles = []
    for article in data["articles"][:ARTICLE_COUNT]:
        title = escape_markdown(article["title"])
        url = f"https://zenn.dev{article['path']}"
        published_at = article["published_at"][:10]
        articles.append(f"- [{title}]({url}) - {published_at}")
    return articles


def replace_section(text: str, name: str, lines: list[str]) -> str:
    pattern = re.compile(
        rf"(<!-- {re.escape(name)} starts -->).*?(<!-- {re.escape(name)} ends -->)",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise RuntimeError(f"README markers for '{name}' were not found")

    block = "\n".join(lines)
    return pattern.sub(
        lambda match: f"{match.group(1)}\n{block}\n{match.group(2)}",
        text,
    )


def main() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    updated = replace_section(readme, "zenn", latest_zenn_articles())
    README_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()

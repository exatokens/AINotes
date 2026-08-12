"""Build content/tree.json from the frontmatter of content/pages/*.md.

Groups pages by week, then by topic (in order of first appearance), sorted by
the ``order`` field. Run after adding or reordering pages:

    python -m ingest.build_tree
"""

import json
from collections import defaultdict

from app import config
from app.content_store import all_pages

WEEK_TITLES = {
    1: "When Meaning Becomes Geometry",
    2: "The Shape of a Decision",
    3: "Measuring the Size of Thoughts: To Chunk, or Not to Chunk?",
    4: "The Understudy: Search-Native Text & Derivative Artifacts",
    5: "When the Library Becomes a City: GraphRAG",
    6: "The Two Gates of the Gatehouse: Guardrails, Grounding, Refusal & Humility",
}


def build():
    """Assemble the tree structure and write it to content/tree.json.

    Returns
    -------
    dict
        The tree that was written: {"weeks": [{week, title, topics: [...]}]}.
    """
    by_week = defaultdict(list)
    for p in all_pages().values():
        by_week[p["week"]].append(p)

    weeks = []
    for wk in sorted(by_week):
        pages = sorted(by_week[wk], key=lambda p: p["order"])
        topics, topic_index = [], {}
        for p in pages:
            if p["topic"] not in topic_index:
                topic_index[p["topic"]] = {"title": p["topic"], "concepts": []}
                topics.append(topic_index[p["topic"]])
            topic_index[p["topic"]]["concepts"].append(
                {"id": p["id"], "title": p["title"], "summary": p.get("summary", "")}
            )
        weeks.append({"week": wk, "title": WEEK_TITLES.get(wk, f"Week {wk}"), "topics": topics})

    tree = {"weeks": weeks}
    config.TREE_FILE.write_text(json.dumps(tree, indent=2))
    n = sum(len(t["concepts"]) for w in weeks for t in w["topics"])
    print(f"tree.json: {len(weeks)} weeks, {n} concept pages")
    return tree


if __name__ == "__main__":
    build()

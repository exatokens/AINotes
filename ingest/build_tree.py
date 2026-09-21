"""Build content/tree.json from the frontmatter of content/pages/*.md.

Groups pages by course, then by week, then by topic (in order of first
appearance), sorted by the ``order`` field. Run after adding or reordering
pages:

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
    7: "The Measure of All Things: Evaluation and the Search Mind",
    8: "The Library in Your Head: Memory, Context, and Retrieval",
    9: "Entitlement-Aware Retrieval and the Library of Many Catalogues",
    10: "The Room as the Corpus: Place, Memory, and Shared Context",
    11: "Cachecraft, Shareability, and the Searchable Commons",
}

AGENTS_WEEK_TITLES = {
    1: "The Three Pillars and the Shape of an Agent",
    2: "From Genie to Prompt: Anatomy and Voice",
    3: "You Cannot Improve What You Cannot Measure",
    4: "The Stochastic Parrot and the Reliability Crisis",
    5: "Agents, Tools, and the Machinery Between Them",
    6: "The Physics of Scale and Cooperation",
    7: "Why and When to Fine-Tune an Agent",
    8: "The Surgery of Fine-Tuning",
    9: "The Escalation Ladder: Prompting to Reinforcement Learning",
    10: "The Vocabulary of Reinforcement Learning",
    11: "Inside Manus, and the Mathematics of Policy Gradients",
    12: "Trust Regions and the Reasoning Breakthrough",
    13: "Coordinating Many Minds: Multi-Agent RL",
}

COURSE_TITLES = {
    config.BEYOND_RAG_COURSE: "Beyond RAG",
    config.AGENTS_COURSE: "AI Agents Bootcamp",
}

COURSE_WEEK_TITLES = {
    config.BEYOND_RAG_COURSE: WEEK_TITLES,
    config.AGENTS_COURSE: AGENTS_WEEK_TITLES,
}

# Courses render in this order in the sidebar, regardless of dict/glob order.
COURSE_ORDER = [config.BEYOND_RAG_COURSE, config.AGENTS_COURSE]


def build_weeks(pages, week_titles):
    """Group one course's pages into the {week, title, topics} list.

    Parameters
    ----------
    pages : list[dict]
    week_titles : dict[int, str]

    Returns
    -------
    list[dict]
    """
    by_week = defaultdict(list)
    for p in pages:
        by_week[p["week"]].append(p)

    weeks = []
    for wk in sorted(by_week):
        wk_pages = sorted(by_week[wk], key=lambda p: p["order"])
        topics, topic_index = [], {}
        for p in wk_pages:
            if p["topic"] not in topic_index:
                topic_index[p["topic"]] = {"title": p["topic"], "concepts": []}
                topics.append(topic_index[p["topic"]])
            topic_index[p["topic"]]["concepts"].append(
                {"id": p["id"], "title": p["title"], "summary": p.get("summary", "")}
            )
        weeks.append({"week": wk, "title": week_titles.get(wk, f"Week {wk}"), "topics": topics})
    return weeks


def build():
    """Assemble the tree structure and write it to content/tree.json.

    Returns
    -------
    dict
        The tree that was written:
        {"courses": [{"course", "title", "weeks": [{week, title, topics: [...]}]}]}.
    """
    by_course = defaultdict(list)
    for p in all_pages().values():
        by_course[p["course"]].append(p)

    courses = []
    order = COURSE_ORDER + [c for c in by_course if c not in COURSE_ORDER]
    for course in order:
        if course not in by_course:
            continue
        weeks = build_weeks(by_course[course], COURSE_WEEK_TITLES.get(course, {}))
        courses.append({
            "course": course,
            "title": COURSE_TITLES.get(course, course),
            "weeks": weeks,
        })

    tree = {"courses": courses}
    config.TREE_FILE.write_text(json.dumps(tree, indent=2))
    n = sum(len(t["concepts"]) for c in courses for w in c["weeks"] for t in w["topics"])
    print(f"tree.json: {len(courses)} course(s), "
          f"{sum(len(c['weeks']) for c in courses)} weeks, {n} concept pages")
    return tree


if __name__ == "__main__":
    build()

"""Fetch YouTube transcripts for every video in youtube_video_links.yaml
(Beyond RAG) and agents_notes/all_weeks_classes_theory (AI Agents Bootcamp).

Writes one JSON file per video to content/sources/transcripts/{video_id}.json
or content/sources/agents_transcripts/{video_id}.json:
    {"video_id": ..., "url": ..., "label": "Week_1_Main_class", "segments": [
        {"text": ..., "start": 12.3, "duration": 4.5}, ...
    ]}

``label`` identifies which week/lesson the link belongs to, which we use
downstream to infer week number and lesson type.

Run:  python -m ingest.fetch_transcripts
"""

import json
import re
import time

import yaml
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from app import config

WEEK_LINE_RE = re.compile(r"^\s*week\s*(\d+)\s*:?\s*(.*)$", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+")


def video_id(url):
    """Extract the 11-char YouTube video id from a watch URL."""
    m = re.search(r"[?&]v=([\w-]{11})", url)
    return m.group(1) if m else url.strip().split("/")[-1]


def parse_beyond_rag_links():
    """Return {label: [url, ...]} from youtube_video_links.yaml."""
    links = yaml.safe_load(config.YOUTUBE_LINKS_FILE.read_text())
    out = {}
    for label, raw in links.items():
        # the YAML has no "-" list markers, so multi-url entries parse as one
        # whitespace-folded string rather than a list — split defensively.
        out[label] = raw if isinstance(raw, list) else raw.split()
    return out


def parse_agents_links():
    """Return {"AgentsWeek_N": [url, ...]} from all_weeks_classes_theory.

    That file is a free-form text dump, not YAML: each "weekN:" line starts a
    group, and any further indented lines (still URLs, no "weekN:" prefix)
    belong to the same group, until the next "weekN:" line. Non-video lines
    (the Manus blog links at the end) are ignored here — see fetch_blogs.py.
    """
    text = config.AGENTS_YOUTUBE_LINKS_FILE.read_text()
    out, current = {}, None
    for line in text.splitlines():
        m = WEEK_LINE_RE.match(line)
        if m:
            current = f"AgentsWeek_{int(m.group(1))}"
            out.setdefault(current, [])
            out[current] += URL_RE.findall(m.group(2))
        elif current and "youtube.com" in line:
            out[current] += URL_RE.findall(line)
    return out


def fetch_all(links, out_dir, api):
    """Download and cache every transcript in a {label: [url, ...]} map."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ok, failed = 0, []
    for label, urls in links.items():
        for url in urls:
            vid = video_id(url)
            out = out_dir / f"{vid}.json"
            if out.exists():
                ok += 1
                continue
            try:
                transcript = api.fetch(vid)
                segments = [
                    {"text": s.text, "start": s.start, "duration": s.duration}
                    for s in transcript.snippets
                ]
                out.write_text(json.dumps(
                    {"video_id": vid, "url": url, "label": label, "segments": segments},
                    indent=2,
                ))
                print(f"  OK   {label:24s} {vid}  ({len(segments)} segments)")
                ok += 1
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                print(f"  SKIP {label:24s} {vid}  {e.__class__.__name__}")
                failed.append((label, url, str(e)))
            except Exception as e:
                print(f"  FAIL {label:24s} {vid}  {e}")
                failed.append((label, url, str(e)))
            time.sleep(0.5)
    return ok, failed


def main():
    """Fetch every transcript for both Beyond RAG and AI Agents Bootcamp."""
    api = YouTubeTranscriptApi()
    ok, failed = 0, []
    for links, out_dir in [
        (parse_beyond_rag_links(), config.TRANSCRIPTS_DIR),
        (parse_agents_links(), config.AGENTS_TRANSCRIPTS_DIR),
    ]:
        o, f = fetch_all(links, out_dir, api)
        ok += o
        failed += f

    print(f"\n{ok} transcripts available, {len(failed)} failed/unavailable.")
    if failed:
        for label, url, err in failed:
            print(f"  - {label}  {url}  ({err})")


if __name__ == "__main__":
    main()

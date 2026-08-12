"""Fetch YouTube transcripts for every video in youtube_video_links.yaml.

Writes one JSON file per video to content/sources/transcripts/{video_id}.json:
    {"video_id": ..., "url": ..., "label": "Week_1_Main_class", "segments": [
        {"text": ..., "start": 12.3, "duration": 4.5}, ...
    ]}

``label`` is the YAML key the link was grouped under (e.g. "Week_2_summary_class"),
which we use downstream to infer week number and lesson type.

Run:  python -m ingest.fetch_transcripts
"""

import json
import re
import time

import yaml
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from app import config


def video_id(url):
    """Extract the 11-char YouTube video id from a watch URL."""
    m = re.search(r"[?&]v=([\w-]{11})", url)
    return m.group(1) if m else url.strip().split("/")[-1]


def main():
    """Download and cache every transcript listed in youtube_video_links.yaml."""
    links = yaml.safe_load(config.YOUTUBE_LINKS_FILE.read_text())
    api = YouTubeTranscriptApi()
    config.TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    ok, failed = 0, []
    for label, raw in links.items():
        # the YAML has no "-" list markers, so multi-url entries parse as one
        # whitespace-folded string rather than a list — split defensively.
        urls = raw if isinstance(raw, list) else raw.split()
        for url in urls:
            vid = video_id(url)
            out = config.TRANSCRIPTS_DIR / f"{vid}.json"
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

    print(f"\n{ok} transcripts available, {len(failed)} failed/unavailable.")
    if failed:
        for label, url, err in failed:
            print(f"  - {label}  {url}  ({err})")


if __name__ == "__main__":
    main()

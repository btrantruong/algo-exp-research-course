#!/usr/bin/env python3
"""
Build the course site into build/index.html (one self-contained page).

Sources
    README.md           title, key facts, course description
    announcements.md    newest-first list of `##` sections
    syllabus.md         project description, grading, project guide (also rendered as #syllabus)
    schedule.yml        calendar skeleton (one row per event)
    lectures/NN/lecture.yml   lecture content, merged into schedule rows by lecture number
    site/site.yml       instructor bios and links, resource sections
    site/template.html, site/style.css, site/app.js

Lecture materials (demos + slides) are published only the day after the lecture
date, and never when the lecture has `hide: true`. Unreleased files are not copied
into build/.

Usage
    .venv/bin/python scripts/build_site.py [--today YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "build"

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

TYPE_LABEL = {
    "intro": "Intro",
    "lecture": "Lecture",
    "mentoring": "Mentoring",
    "presentation": "Presentation",
    "deadline": "Due",
    "break": "Break",
    "independent": "Independent work",
}
NEW_TAB = ' target="_blank" rel="noopener"'  # PDFs open in the browser viewer, not as downloads
UPCOMING_TYPES = {"intro", "lecture", "mentoring", "presentation", "deadline"}


# ---------------------------------------------------------------- helpers

def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


LIST_ITEM = re.compile(r"\s*(\d+\.|[-*]) ")


def fix_lists(text: str) -> str:
    """Python-Markdown wants a blank line before a list and 4-space nesting."""
    text = re.sub(r"(?m)^ {3}([-*] )", r"    \1", text)
    out: list[str] = []
    for line in text.splitlines():
        prev = out[-1] if out else ""
        if LIST_ITEM.match(line) and prev.strip() and not LIST_ITEM.match(prev) and not prev.startswith(" "):
            out.append("")
        out.append(line)
    return "\n".join(out)


def md(text: str) -> str:
    return markdown.markdown(fix_lists(text), extensions=["tables", "sane_lists"])


def md_inline(text: str) -> str:
    out = md(text).strip()
    return re.sub(r"^<p>(.*)</p>$", r"\1", out, flags=re.DOTALL)


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def sections(text: str, level: int = 2) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) pairs at headings of exactly `level`."""
    marker = "#" * level + " "
    out: list[tuple[str, list[str]]] = []
    for line in text.splitlines():
        if line.startswith(marker):
            out.append((line[len(marker):].strip(), []))
        elif out:
            out[-1][1].append(line)
    return [(h, "\n".join(b).strip()) for h, b in out]


def find_section(secs: list[tuple[str, str]], prefix: str) -> str:
    for heading, body in secs:
        if heading.lower().startswith(prefix.lower()):
            return body
    sys.exit(f"section starting with '{prefix}' not found")


def fmt_date(d: dt.date, year: bool = True) -> str:
    s = f"{d.day} {MONTHS[d.month - 1]}"
    return f"{s} {d.year}" if year else s


# ---------------------------------------------------------------- content

def read_readme() -> dict:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    title = next(l[2:].strip() for l in text.splitlines() if l.startswith("# "))
    facts = re.findall(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*$", text, flags=re.M)
    description = find_section(sections(text), "Course Description")
    return {"title": title, "facts": facts, "description": description}


def read_announcements() -> list[tuple[str, str]]:
    out = []
    for heading, body in sections((ROOT / "announcements.md").read_text(encoding="utf-8")):
        lines = []
        for line in body.splitlines():
            if line.strip() == "---":
                break
            lines.append(line)
        out.append((heading, "\n".join(lines).strip()))
    return out


def read_schedule(today: dt.date) -> list[dict]:
    rows = load_yaml(ROOT / "schedule.yml")["rows"]
    lectures = {}
    for path in sorted((ROOT / "lectures").glob("*/lecture.yml")):
        data = load_yaml(path)
        data["dir"] = path.parent
        lectures[int(data["lecture"])] = data

    for row in rows:
        n = row.get("lecture")
        lec = lectures.get(n) if n is not None else None
        row["lec"] = lec
        row["title"] = (lec or {}).get("title") or row.get("title") or (f"Lecture {n}" if n is not None else "")
        row["last"] = row.get("end") or row["date"]
        row["released"] = bool(lec) and today > row["date"] and not lec.get("hide", False)

    rows.sort(key=lambda r: r["date"])  # stable: ties keep file order

    next_row = None
    for row in rows:
        row["past"] = row["last"] < today
        if next_row is None and not row["past"] and row["type"] in UPCOMING_TYPES:
            next_row = row
    for row in rows:
        row["is_next"] = row is next_row
    return rows


# ---------------------------------------------------------------- materials

def publish_materials(row: dict) -> list[tuple[str, str, str]]:
    """Copy released files into build/ and return (label, href, desc) links."""
    lec = row["lec"]
    n = lec["dir"].name
    links = []
    for m in lec.get("materials") or []:
        src = lec["dir"] / m["file"]
        if not src.exists():
            print(f"warning: lecture {n}: missing {src.relative_to(ROOT)}", file=sys.stderr)
            continue
        dst = OUT / "lectures" / n / m["file"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if m.get("listed", True):
            links.append((m["label"], f"lectures/{n}/{m['file']}", m.get("desc", "")))

    slides = lec.get("slides") or []
    for name in [slides] if isinstance(slides, str) else slides:
        src = ROOT / "slides" / name
        if not src.exists():
            print(f"warning: lecture {n}: missing slides/{name} (run scripts/slides_to_pdf.py)", file=sys.stderr)
            continue
        dst = OUT / "slides" / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        ext = src.suffix.lstrip(".").upper()
        links.append(("Slides", f"slides/{name}", f"{ext} · {src.stat().st_size / 1e6:.1f} MB"))
    return links


def lecture_details(row: dict) -> str:
    lec = row["lec"]
    parts = []
    if lec and lec.get("summary"):
        parts.append(f'<p class="summary">{md_inline(lec["summary"])}</p>')

    has_materials = bool(lec and (lec.get("materials") or lec.get("slides")))
    if row["released"] and has_materials:
        items = "".join(
            f'<li><a href="{esc(href)}"{NEW_TAB if href.endswith(".pdf") else ""}><strong>{esc(label)}</strong>'
            f'{f"<span>{esc(desc)}</span>" if desc else ""}</a></li>'
            for label, href, desc in publish_materials(row)
        )
        parts.append(f'<ul class="materials">{items}</ul>')
    elif has_materials:
        parts.append('<p class="pending">Slides and demos will be posted after the session.</p>')
    if not parts:
        return ""
    return (
        '<details class="lecture-details">'
        f'<summary>Details &amp; materials</summary>{"".join(parts)}</details>'
    )


# ---------------------------------------------------------------- render: schedule

def render_row(row: dict) -> str:
    d, kind = row["date"], row["type"]
    state = "past" if row["past"] else "upcoming"
    milestone_only = kind == "deadline"
    note = f'<span class="tag">{esc(row["note"])}</span>' if row.get("note") else ""

    meta = []
    if not milestone_only:
        badge = f"Lecture {row['lecture']}" if kind == "lecture" else TYPE_LABEL[kind]
        meta.append(f'<span class="badge b-{kind}">{esc(badge)}</span>')
        lead = row.get("lead")
        if lead and lead != "/":
            meta.append(f'<span class="tag">Lead: {esc(lead)}</span>')
        if kind in {"intro", "lecture"}:
            where = "Zoom" if row.get("location") == "zoom" else "BZW/A255"
            meta.append(f'<span class="tag">{where}</span>')
        if note and kind != "break":
            meta.append(note)
    if row["is_next"]:
        meta.append('<span class="badge b-next">Next up</span>')

    title = esc(row["title"]) or '<span class="muted">—</span>'
    if kind == "break" and row.get("note"):
        title += f" ({esc(row['note'])})"
    desc = f'<p class="desc">{esc(row["desc"])}</p>' if row.get("desc") else ""

    if row.get("end"):
        when = f'{fmt_date(d, False)} – {fmt_date(row["end"])}'
        date_block = (
            f'<div class="date"><span class="dow">From</span><span class="day">{d.day}</span>'
            f'<span class="mon">{MONTHS[d.month - 1]}</span></div>'
        )
        desc = f'<p class="desc">{esc(when)}</p>' + desc
    else:
        date_block = (
            f'<div class="date"><span class="dow">{DAYS[d.weekday()]}</span><span class="day">{d.day}</span>'
            f'<span class="mon">{MONTHS[d.month - 1]} {d.year}</span></div>'
        )

    milestone = ""
    if row.get("milestone"):
        extra = f" {note}" if milestone_only else ""
        milestone = (
            '<div class="due-card"><span class="due-label">Due</span>'
            f'<strong>{esc(row["milestone"])}</strong>{extra}</div>'
        )

    details = lecture_details(row) if kind == "lecture" else ""
    row_id = f' id="lecture-{row["lecture"]}"' if kind == "lecture" else ""
    return (
        f'<li{row_id} class="row t-{kind} {state}{" is-next" if row["is_next"] else ""}">{date_block}'
        f'<div class="row-body"><div class="meta">{"".join(meta)}</div>'
        f'<h3>{title}</h3>{desc}{details}</div>'
        f'<div class="milestone">{milestone}</div></li>'
    )


def render_schedule(rows: list[dict]) -> str:
    return (
        '<h1>Schedule</h1>'
        '<p class="intro">The schedule will be adjusted as we go, so please check it regularly for '
        "updates. Slides and demos are posted after each session.</p>"
        '<p class="intro"><strong>Note:</strong> Reading assignments should be completed before class. '
        "These won’t be graded but there may be a quiz on the reading material, and students are "
        "expected to participate in class discussions about the materials.</p>"
        '<div class="timeline-head" aria-hidden="true"><span>Date</span><span>Session</span>'
        "<span>Milestone</span></div>"
        f'<ol class="timeline">{"".join(render_row(r) for r in rows)}</ol>'
        '<p class="footer-note">The Semester 2 schedule will be added later.</p>'
    )


# ---------------------------------------------------------------- render: other tabs

def render_facts(facts: list[tuple[str, str]], groups: list[dict]) -> str:
    """Key facts from the README table, arranged in the groups named in site.yml."""
    values = dict(facts)
    used: set[str] = set()
    blocks = []
    for group in groups:
        items = []
        for key in group["items"]:
            if key not in values:
                print(f"warning: fact '{key}' not found in README.md", file=sys.stderr)
                continue
            used.add(key)
            items.append(f"<dt>{esc(key)}</dt><dd>{md_inline(values[key])}</dd>")
        blocks.append(f'<div class="fact-group"><h2>{esc(group["title"])}</h2><dl>{"".join(items)}</dl></div>')
    leftover = [k for k, _ in facts if k not in used]
    if leftover:
        print(f"warning: facts not in any group: {leftover}", file=sys.stderr)
    return f'<div class="facts">{"".join(blocks)}</div>'


def render_home(readme: dict, announcements: list, rows: list[dict], cfg: dict) -> str:
    facts = render_facts(readme["facts"], cfg.get("fact_groups", []))

    latest = ""
    if announcements:
        heading, body = announcements[0]
        latest = (
            '<section class="card announce"><p class="eyebrow">Latest announcement</p>'
            f"<h2>{esc(heading)}</h2>{md(body)}</section>"
        )
    archive = ""
    if len(announcements) > 1:
        items = "".join(
            f"<article><h3>{esc(h)}</h3>{md(b)}</article>" for h, b in announcements[1:]
        )
        archive = f'<details class="card archive"><summary>Earlier announcements</summary>{items}</details>'

    nxt = next((r for r in rows if r["is_next"]), None)
    next_html = ""
    if nxt:
        href = f'#lecture-{nxt["lecture"]}' if nxt["type"] == "lecture" else "#schedule"
        label = f'Lecture {nxt["lecture"]}' if nxt["type"] == "lecture" else TYPE_LABEL[nxt["type"]]
        next_html = (
            '<section class="card next-up"><p class="eyebrow">Next session</p>'
            f'<h2>{esc(nxt["title"] or nxt["milestone"])}</h2><p class="muted">{esc(label)} · '
            f'{DAYS[nxt["date"].weekday()]} {fmt_date(nxt["date"])}</p>'
            f'<a class="button" href="{href}">See details</a></section>'
        )

    return (
        f'<h1>{esc(readme["title"])}</h1>'
        f'<div class="lede">{md(readme["description"])}'
        '<p class="lede-link"><a href="#syllabus">Full syllabus →</a></p></div>'
        f'{facts}'
        f'<div class="two-col"><div>{latest}{archive}</div><div>{next_html}</div></div>'
    )


def accordion(title: str, blurb: str, body: str) -> str:
    return (
        '<details class="res"><summary>'
        f'<span class="res-title">{esc(title)}</span><span class="res-blurb">{esc(blurb)}</span></summary>'
        f'<div class="card doc res-body">{body}</div></details>'
    )


def render_resources(syllabus: list, cfg: dict) -> str:
    project = find_section(syllabus, "Understanding")
    guide = find_section(syllabus, "How to choose a project")
    rows = [
        accordion(
            "Choosing a project",
            "Your research project and how to scope it.",
            f"<h3>Your research project</h3>{md(project)}<h3>How to choose a project?</h3>{md(guide)}",
        )
    ]
    for sec in cfg.get("resources", []):
        links = sec.get("links") or []
        if links:
            items = []
            for link in links:
                note = f" — {esc(link['note'])}" if link.get("note") else ""
                items.append(f'<li><a href="{esc(link["url"])}">{esc(link["label"])}</a>{note}</li>')
            body = "<ul>" + "".join(items) + "</ul>"
        else:
            body = '<p class="pending">Curated links coming soon.</p>'
        rows.append(accordion(sec["title"], sec.get("blurb", ""), body))
    return (
        '<h1>Resources</h1>'
        '<p class="intro">Guidance for your project, plus curated links and references.</p>'
        f'<div class="accordion">{"".join(rows)}</div>'
    )


def render_syllabus() -> str:
    text = (ROOT / "syllabus.md").read_text(encoding="utf-8")
    return (
        '<p class="back"><a href="#home">← Back to Home</a></p>'
        f'<article class="card doc syllabus">{md(text)}</article>'
    )


def render_instructors(cfg: dict) -> str:
    cards = []
    for person in cfg.get("instructors", []):
        name = person["name"]
        initials = "".join(w[0] for w in name.split()[:2] if w[0].isalpha())
        heading = f'<a href="{esc(person["url"])}">{esc(name)}</a>' if person.get("url") else esc(name)
        cards.append(
            f'<article class="card person"><div class="avatar" aria-hidden="true">{esc(initials)}</div>'
            f"<div><h2>{heading}</h2><p>{esc(person.get('bio', ''))}</p></div></article>"
        )
    return (
        '<h1>Instructors</h1>'
        f'<div class="people">{"".join(cards)}</div>'
    )


# ---------------------------------------------------------------- main

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--today", help="override today's date (YYYY-MM-DD), for previews")
    args = parser.parse_args()
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()

    cfg = load_yaml(SITE / "site.yml")
    readme = read_readme()
    announcements = read_announcements()
    syllabus = sections((ROOT / "syllabus.md").read_text(encoding="utf-8"))
    rows = read_schedule(today)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    page = (SITE / "template.html").read_text(encoding="utf-8")
    values = {
        "page_title": cfg["short_title"],
        "short_title": esc(cfg["short_title"]),
        "css": (SITE / "style.css").read_text(encoding="utf-8"),
        "js": (SITE / "app.js").read_text(encoding="utf-8"),
        "home": render_home(readme, announcements, rows, cfg),
        "syllabus": render_syllabus(),
        "schedule": render_schedule(rows),
        "resources": render_resources(syllabus, cfg),
        "instructors": render_instructors(cfg),
        "repo": esc(cfg["repo"]),
        "built": fmt_date(today),
    }
    for key, value in values.items():
        page = page.replace("{{" + key + "}}", value)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)}/index.html for {today.isoformat()}")


if __name__ == "__main__":
    main()

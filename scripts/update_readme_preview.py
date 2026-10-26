#!/usr/bin/env python3
"""
Sync the Latest Announcement preview in README.md with announcements.md.

Reads the first ## section from announcements.md, converts it to a
markdown blockquote, and writes it between the HTML comment markers:

    <!-- LATEST_ANNOUNCEMENT_START -->
    ...generated content...
    <!-- LATEST_ANNOUNCEMENT_END -->

Run directly (`python3 scripts/update_readme_preview.py`) or via the
pre-commit hook, which calls this script automatically on every commit.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANNOUNCEMENTS = ROOT / "announcements.md"
README = ROOT / "README.md"

START = "<!-- LATEST_ANNOUNCEMENT_START -->"
END   = "<!-- LATEST_ANNOUNCEMENT_END -->"


def first_section(text: str) -> tuple[str, str]:
    """Return (heading, body) of the first ## section in the file."""
    lines = text.splitlines()

    # Find the line index of the first ## heading (## = section, not # title)
    start = next(
        (i for i, line in enumerate(lines) if re.match(r"^## ", line)),
        None,
    )
    if start is None:
        sys.exit("announcements.md: no ## section found")

    heading = lines[start][3:].strip()   # strip leading "## "

    # Collect body lines until the next ## section or a --- divider
    body: list[str] = []
    for line in lines[start + 1:]:
        if re.match(r"^## ", line) or line.strip() == "---":
            break
        body.append(line)

    # Remove trailing blank lines
    while body and not body[-1].strip():
        body.pop()

    return heading, "\n".join(body)


def as_blockquote(heading: str, body: str) -> str:
    """Wrap heading + body as a markdown blockquote (> lines)."""
    lines = [f"> **{heading}**"]
    if body.strip():
        lines.append(">")
        for line in body.splitlines():
            # Preserve blank lines inside the blockquote as bare ">"
            lines.append(f"> {line}" if line.strip() else ">")
    return "\n".join(lines)


def inject(readme: str, block: str) -> str:
    """Replace everything between the START and END markers."""
    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END), re.DOTALL
    )
    if not pattern.search(readme):
        sys.exit(
            "README.md: markers not found.\n"
            "Add <!-- LATEST_ANNOUNCEMENT_START --> and "
            "<!-- LATEST_ANNOUNCEMENT_END --> around the preview block."
        )
    return pattern.sub(f"{START}\n{block}\n{END}", readme)


def main() -> None:
    heading, body = first_section(ANNOUNCEMENTS.read_text())
    block = as_blockquote(heading, body)

    readme = README.read_text()
    updated = inject(readme, block)

    if updated == readme:
        print("README.md already up to date.")
        return

    README.write_text(updated)
    print(f"README.md preview updated → {heading}")


if __name__ == "__main__":
    main()

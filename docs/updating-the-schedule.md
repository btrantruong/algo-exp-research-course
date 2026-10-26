# Updating the schedule

The Schedule tab on the course site is built from one file: [`schedule.yml`](../schedule.yml).

## How to edit

1. Open [`schedule.yml`](../schedule.yml) on GitHub and click the **pencil icon** (top right).
2. Make your change.
3. Click **Commit changes…** and commit directly to `main`.
4. The site redeploys automatically (see below).

## How the site redeploys

- **What triggers it:** any commit to `main`, whether you edit on GitHub or merge a pull request.
  If you edit on a branch, nothing changes until the branch is merged.
- **How long it takes:** about 2 minutes. Open the **Actions** tab and look for "Deploy course site":
  a green ✓ means it is live. A red ✗ means the build failed (usually a typo) and the old site stays up.
  Open the run to see the error, then fix the file.
- **Daily rebuild:** the site also rebuilds by itself every day at about 03:00 UTC.
  That is how slides and demos appear the morning after a lecture, even if nobody edits anything.
- **If the page looks unchanged:** hard-refresh (Cmd/Ctrl+Shift+R) or open a private window,
  because browsers cache the page. If the run is green and it still looks old, tell Bao.
- **Redeploy by hand (optional):** Actions → "Deploy course site" → **Run workflow**. This needs write access.

## One row

```yaml
  - date: 2026-12-17            # YYYY-MM-DD (rows can be in any order)
    type: mentoring             # intro | lecture | mentoring | presentation | break | independent | deadline
    title: Optional mentoring session
    desc: One-line detail       # optional
    milestone: Submission of Intro draft   # optional: shows a red "Due" card on that date
    lead: Kamil                 # optional: "/" or leave out if nobody leads
    location: zoom              # optional: zoom (default is the room)
    note: TBC                   # optional: small tag
```

Keep the two-space indent, the `-` in front of each row, and the `key: value` spacing.
If a value contains a colon (`:`), put it in quotes: `title: "Part 1: Basics"`.

## Common changes

- **Move or rename a session:** change `date` or `title`.
- **Add a deadline:** add `milestone: What students must hand in` to the row on that date.
  If there is no session that day, add a new row with `type: deadline` and only `date` and `milestone`.
- **Add or remove a no-class day:** add or delete a row with `type: break`.
- **Cancel a session:** delete its row (or change it to `type: break`).

## Lectures (4–6 are yours)

A lecture row has `type: lecture` and `lecture: 4`. Its content goes in `lectures/04/lecture.yml`.
Create it with **Add file → Create new file**, using the name `lectures/04/lecture.yml`:

```yaml
lecture: 4
title: Your lecture title
summary: One or two sentences on what the lecture covers.
hide: false
```

Then, in `schedule.yml`, delete the placeholder `title:` and `desc:` lines on the row for lecture 4.

**Slides:** export the slides as PDF (PowerPoint/Keynote: *Export as PDF*), then use
**Add file → Upload files** to put `NN.pdf` in the `slides/` folder. Add `slides: 04.pdf` to the lecture's `lecture.yml`.
The slides appear on the site the day after the lecture. Add `hide: true` to keep them off the site.

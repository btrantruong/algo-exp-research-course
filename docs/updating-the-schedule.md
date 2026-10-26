# Updating the schedule

The Schedule tab on the course site is built from one file: [`schedule.yml`](../schedule.yml).

## How to edit

1. Open [`schedule.yml`](../schedule.yml) on GitHub and click the **pencil icon** (top right).
2. Make your change.
3. Click **Commit changes…** and commit directly to `main`.
4. The site updates in about 2 minutes. Check the **Actions** tab: a green ✓ means it is live.
   A red ✗ means there is a typo; the old site stays up. Open the run to see the error, then fix the file.

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

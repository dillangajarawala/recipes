#!/usr/bin/env python3
"""
Recipe site builder.
Reads markdown files from src/, outputs a static HTML site to _site/.
Run: python build.py
"""

import os
import re
import shutil
from pathlib import Path

SRC_DIR = Path("src")
OUT_DIR = Path("_site")

# ── CSS ────────────────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:      #121a11;
    --surface: #1c2a1b;
    --text:    #ece8d4;
    --muted:   #7a9168;
    --accent:  #c9a84c;
    --border:  #243022;
    --tag-bg:  #182217;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.65;
    font-size: 17px;
}

/* ── Header ── */

.site-header {
    background: #0d1410;
    border-bottom: 1px solid var(--accent);
    padding: 0.9rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.site-header .site-name {
    color: var(--accent);
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-decoration: none;
}

.site-header .back-link {
    color: var(--muted);
    font-size: 0.82rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    text-decoration: none;
    transition: color 0.15s;
}

.site-header .back-link:hover { color: var(--accent); }

/* ── Container ── */

.container {
    max-width: 760px;
    margin: 0 auto;
    padding: 3rem 1.5rem 6rem;
}

/* ── Index hero ── */

.hero {
    text-align: center;
    padding: 3rem 0 3.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.75rem;
}

.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1rem;
}

.hero-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.1;
    color: var(--text);
    margin-bottom: 1rem;
}

.hero-blurb {
    color: var(--muted);
    font-size: 0.97rem;
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.7;
}

.index-count {
    color: var(--muted);
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.recipe-list {
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--surface);
}

.recipe-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 1.4rem;
    text-decoration: none;
    color: var(--text);
    border-bottom: 1px solid var(--border);
    transition: background 0.15s, transform 0.2s cubic-bezier(0.2, 0, 0.2, 1), box-shadow 0.2s;
    position: relative;
    z-index: 0;
}

.recipe-row:first-child { border-radius: 10px 10px 0 0; }
.recipe-row:last-child  { border-radius: 0 0 10px 10px; border-bottom: none; }

.recipe-row:hover {
    background: #1f2e1e;
    transform: perspective(700px) translateY(-3px) rotateX(2deg);
    box-shadow: 0 8px 24px rgba(0,0,0,0.55), 0 2px 8px rgba(201,168,76,0.12);
    z-index: 1;
}

.recipe-row-name {
    font-size: 1rem;
    font-weight: 500;
}

.recipe-row-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-shrink: 0;
    margin-left: 1rem;
}

.recipe-row-yield {
    font-size: 0.82rem;
    color: var(--muted);
}

.recipe-row-arrow {
    color: var(--accent);
    font-size: 1rem;
    opacity: 0.8;
}

/* ── Recipe page ── */

.recipe-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 0.4rem;
}

.recipe-yield {
    color: var(--muted);
    font-size: 0.9rem;
    margin-bottom: 2.75rem;
    font-style: italic;
}

.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.85rem;
}

/* Ingredients */

.ingredients-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.25rem 1.4rem;
    margin-bottom: 2.75rem;
}

.ingredient-row {
    display: flex;
    align-items: baseline;
    gap: 0.7rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 1rem;
}

.ingredient-row:last-child { border-bottom: none; }

.ingredient-dot {
    color: var(--accent);
    font-size: 1.3rem;
    line-height: 1;
    flex-shrink: 0;
    margin-top: 0.05rem;
}

/* Instructions */

.steps { margin-bottom: 2.75rem; }

.step {
    display: grid;
    grid-template-columns: 2.4rem 1fr;
    gap: 1.1rem;
    margin-bottom: 1.75rem;
    align-items: start;
}

.step-num {
    width: 2.4rem;
    height: 2.4rem;
    border-radius: 50%;
    background: var(--accent);
    color: #0d1410;
    font-weight: 700;
    font-size: 0.88rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 0.15rem;
}

.step-body { padding-top: 0.3rem; }

.step-name {
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: var(--text);
}

.step-bullets { list-style: none; }

.step-bullets li {
    position: relative;
    padding: 0.25rem 0 0.25rem 1.1rem;
    font-size: 0.97rem;
    line-height: 1.6;
    color: var(--text);
    opacity: 0.85;
}

.step-bullets li::before {
    content: "–";
    position: absolute;
    left: 0;
    color: var(--muted);
}

/* Notes */

.notes {
    background: var(--tag-bg);
    border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
    padding: 1.1rem 1.4rem;
    font-size: 0.93rem;
    color: var(--muted);
    font-style: italic;
    line-height: 1.7;
}

/* ── Responsive ── */

@media (max-width: 580px) {
    body { font-size: 16px; }
    .recipe-title { font-size: 2rem; }
    .hero-title   { font-size: 2.4rem; }
    .container    { padding: 2rem 1rem 5rem; }
    .site-header  { padding: 0.75rem 1rem; }
}
"""

# ── Parser ─────────────────────────────────────────────────────────────────────

def parse_recipe(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()

    title = ""
    yield_text = ""
    ingredients: list[str] = []
    steps: list[dict] = []   # [{"name": str, "bullets": [str]}]
    notes = ""

    section = None
    current_step = None

    for raw in lines:
        line = raw.rstrip()

        if line.startswith("# "):
            title = line[2:].strip()

        elif re.match(r"^\*Yield:", line):
            yield_text = re.sub(r"^\*Yield:\s*", "", line).rstrip("* ").strip()

        elif re.sub(r"\s+$", "", line) in ("**Ingredients:**", "**Ingredients**"):
            section = "ingredients"

        elif re.sub(r"\s+$", "", line) in ("**Instructions:**", "**Instructions**"):
            section = "instructions"

        elif section == "ingredients" and line.startswith("* "):
            ingredients.append(line[2:].strip())

        elif section == "instructions" and re.match(r"^\d+\.\s+\*\*", line):
            name = re.sub(r"^\d+\.\s+\*\*(.+?)\*\*.*", r"\1", line).rstrip(":").strip()
            current_step = {"name": name, "bullets": []}
            steps.append(current_step)

        elif section == "instructions" and re.match(r"^\s+\*\s", line) and current_step:
            current_step["bullets"].append(re.sub(r"^\s+\*\s+", "", line).strip())

        elif re.match(r"^\*[Nn]otes?:", line):
            notes = re.sub(r"^\*[Nn]otes?:\s*", "", line).rstrip("* ").strip()

    return {
        "title": title,
        "yield": yield_text,
        "ingredients": ingredients,
        "steps": steps,
        "notes": notes,
    }


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s


def esc(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


# ── HTML renderers ─────────────────────────────────────────────────────────────

def render_index(recipes: list[dict]) -> str:
    rows = ""
    for r in sorted(recipes, key=lambda x: x["title"]):
        href = f"{slugify(r['title'])}.html"
        yield_span = f'<span class="recipe-row-yield">{esc(r["yield"])}</span>' if r["yield"] else ""
        rows += f"""
        <a class="recipe-row" href="{href}">
            <span class="recipe-row-name">{esc(r["title"])}</span>
            <span class="recipe-row-right">
                {yield_span}
                <span class="recipe-row-arrow">→</span>
            </span>
        </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dillan's Recipes</title>
    <style>{CSS}</style>
</head>
<body>
    <header class="site-header">
        <a class="site-name" href="./">Dillan's Recipes</a>
    </header>
    <main class="container">
        <div class="hero">
            <h1 class="hero-title">Dillan's Recipes</h1>
            <p class="hero-blurb">You've found my recipe collection! Here's my small but mighty list of vegetarian recipes built around high protein and fiber. 
            Each one makes at least 3 servings, so you can get away with only cooking a couple times a week and having your food last. I'm trying to get better about testing out new things, 
            so when I find a recipe that works well, I'll post it here!</p>
        </div>
        <p class="index-count">{len(recipes)} recipes</p>
        <nav class="recipe-list">{rows}
        </nav>
    </main>
</body>
</html>"""


def render_recipe(r: dict) -> str:
    # Ingredients
    ing_html = ""
    for item in r["ingredients"]:
        ing_html += f"""
            <div class="ingredient-row">
                <span class="ingredient-dot">·</span>
                <span>{esc(item)}</span>
            </div>"""

    # Steps
    steps_html = ""
    for i, step in enumerate(r["steps"], 1):
        bullets = "".join(f"\n                    <li>{esc(b)}</li>" for b in step["bullets"])
        steps_html += f"""
        <div class="step">
            <div class="step-num">{i}</div>
            <div class="step-body">
                <div class="step-name">{esc(step["name"])}</div>
                <ul class="step-bullets">{bullets}
                </ul>
            </div>
        </div>"""

    yield_html = f'<p class="recipe-yield">{esc(r["yield"])}</p>' if r["yield"] else ""
    notes_html = f'<div class="notes">{esc(r["notes"])}</div>' if r["notes"] else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(r["title"])} — Dillan's Recipes</title>
    <style>{CSS}</style>
</head>
<body>
    <header class="site-header">
        <a class="site-name" href="./">Dillan's Recipes</a>
        <a class="back-link" href="./">← All Recipes</a>
    </header>
    <main class="container">
        <h1 class="recipe-title">{esc(r["title"])}</h1>
        {yield_html}
        <p class="section-label">Ingredients</p>
        <div class="ingredients-card">{ing_html}
        </div>

        <p class="section-label">Instructions</p>
        <div class="steps">{steps_html}
        </div>

        {notes_html}
    </main>
</body>
</html>"""


# ── Main ───────────────────────────────────────────────────────────────────────

def build():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()

    recipes = []
    for md_file in sorted(SRC_DIR.glob("*.md")):
        r = parse_recipe(md_file)
        if not r["title"]:
            print(f"  Skipped (no title): {md_file.name}")
            continue
        recipes.append(r)
        out = OUT_DIR / f"{slugify(r['title'])}.html"
        out.write_text(render_recipe(r), encoding="utf-8")
        print(f"  ✓ {out.name}")

    (OUT_DIR / "index.html").write_text(render_index(recipes), encoding="utf-8")
    print(f"  ✓ index.html  ({len(recipes)} recipes)")
    print("\nDone — output in _site/")


if __name__ == "__main__":
    build()

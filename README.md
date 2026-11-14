# Dillan's Recipes

A static recipe site built from markdown files by `build.py` (Python 3, standard library only).

## Building

```
python3 build.py
open _site/index.html
```

## Deploying

Pushing to `main` runs the GitHub Actions workflow, which builds the site and publishes `_site/` to gh-pages.

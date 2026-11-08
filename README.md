# Michael Schultz — personal research website

Public website: https://schultzheidelberg.github.io/

A lightweight static academic website with research, publications, projects,
open data, code, and contact information. It has no login or server dependency.

## Build and preview

Requires Python 3 and its standard library only.

```sh
python3 build.py
python3 -m http.server 8000 --directory docs
```

Open http://localhost:8000/ to preview. Content and templates are in `build.py`;
styles, scripts, and images are in `assets/`. The generated `docs/` directory is
committed so GitHub Pages can publish it directly. Run the build again after any
source changes and commit both source files and generated output.

## Publications

`data/publications.json` is the source for the complete publications page and
the selected journal articles on the home page. `bibliography.py` renders all
records with their output types, verified years, source links, and notes.
Search and type/year filters enhance the static list; all records remain
readable without JavaScript.

`data/research-metrics.json` stores the source-labelled h-index shown first in
the publications summary. This is a dated snapshot, not a live counter. Check the
linked author profile against the ORCID before updating the value and date.

Keep the public PDF, BibTeX, CSV, JSON, and Markdown exports in `data/` together.
After updating the bibliography, run `python3 export_bibliography.py` before the
website build. Exporting the PDF requires ReportLab and DejaVu Sans fonts; normal
website builds still use only the standard library.
The build copies these five files to `docs/downloads/` for public access without
a login. The PDF is the public bibliography, not the separate private manuscript
review. Publisher/repository PDFs are linked rather than copied into this site.

Accepted future conference contributions are in `data/upcoming.json`, and current
submission/revision metadata is in `data/manuscripts.json`. Both appear in separate
sections and are excluded from completed-output and journal-article totals.
Private correspondence and editorial attachments are not included in this repository.

## Publish with GitHub Pages

Use the public repository `schultzheidelberg/schultzheidelberg.github.io`.
In **Settings → Pages**, select **Deploy from a branch**, the **main** branch,
and the **/docs** folder, then save. GitHub serves the site at the address above.
No custom workflow, custom domain, API keys, or viewer authentication is needed.
The `docs/.nojekyll` file tells GitHub Pages to serve the generated files as-is.

Image credits and research sources are documented on the site's `/sources/` page.

## Printable portfolio

`data/Michael_Schultz_Portfolio.pdf` is a four-page A4 handout with white paper,
project figures, selected publications, clickable links and vector QR codes to
the stable public homepage. Its edition is November 2026. The homepage and CV
link to `/downloads/Michael_Schultz_Portfolio.pdf`.

To refresh the approved copy or imagery, edit `export_portfolio.py`, then run:

```sh
python3 export_portfolio.py
python3 build.py
```

The exporter uses ReportLab, Pillow, DejaVu Sans and Liberation Serif. Ordinary
site builds only copy the existing PDF and still use the Python standard library.
After regenerating, inspect all four rendered pages and check the QR codes before
publishing. Print on A4 at actual size; duplex printing uses the long-edge setting.

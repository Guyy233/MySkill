# Integration Roadmap

Use this file when deciding what to wire into the skill first.

## Current machine state

As of 2026-04-09, the local machine already has:

- `pdfimages`
- `pdftoppm`
- `python`
- workspace-local `Docling` install under `D:\study\A_finalyear_prj\.pydeps\paper-reading-html`
- workspace-local `Marker` install under `D:\study\A_finalyear_prj\.pydeps\paper-reading-marker`

It does **not** currently have:

- `mineru`
- `pymupdf4llm`
- `rapid_latex_ocr`
- `java` for `pdffigures2`

So the next useful move is no longer ?install any parser at all?.
The next useful move is to make the HTML generator consume the stronger extraction artifacts instead of relying on hand-written source placeholders.

## Recommended integration order

### Step 1: Default parser path

Integrate **Docling** first.
It is the best default technical fit and the cleanest licensing default.

### Step 2: Better figure path

Keep `pdfimages` as a zero-dependency fallback.
Add **pdffigures2** when figure units and captions matter enough to justify the Java dependency.

### Step 3: Formula repair path

Keep normal text-based formula reconstruction first.
Add **pix2tex** only for formula-as-image failures.

### Step 4: Scholarly structure path

Add **GROBID** when citation spans, references, or clean section hierarchy become important for the reading page.

### Step 5: Hard-PDF escape hatch

Support **Marker** and **MinerU** as optional backends.
Do not make either one the mandatory default.

## Practical meaning for this skill

This skill should not be written as if one parser will solve every PDF.
It should:

- probe available backends
- run the best available backend in priority order
- keep all backend outputs in separate subfolders
- build a manifest that the HTML renderer can consume
- make the reader-facing page independent from any single parser implementation

## Important boundary

No open-source parser will automatically produce a truly good guided reading page.
The parser fixes structure.
The skill still needs strong segmentation rules and better annotation logic to make the paper understandable block by block.


## Local workspace installation pattern

When backends are installed with `pip install --target ...` instead of into the main Python environment,
set these environment variables before running the pipeline:

- `PAPER_READING_HTML_EXTRA_SITE`: one or more package directories, separated by the platform path separator
- `PAPER_READING_HTML_MARKER_BIN`: optional explicit path to `marker_single.exe` when Marker is installed locally

Example on Windows:

```powershell
$env:PAPER_READING_HTML_EXTRA_SITE = 'D:\study\A_finalyear_prj\.pydeps\paper-reading-html;D:\study\A_finalyear_prj\.pydeps\paper-reading-marker'
$env:PAPER_READING_HTML_MARKER_BIN = 'D:\study\A_finalyear_prj\.pydeps\paper-reading-marker\bin\marker_single.exe'
python scripts\extract_pdf_pipeline.py paper.pdf --out-dir out
```

## Current evidence from repro PDFs

On the repro papers tested on 2026-04-09:

- `Docling` improved section order, figure-caption binding, and body structure
- `Marker` produced materially better extracted formulas and true figure image files
- `Docling` is a good structural default, but `Marker` is the better fallback for formula-heavy pages in this project

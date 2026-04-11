# Open-Source Backends

Use this file when page quality depends more on extraction than on prompt wording.

Checked against GitHub on **2026-04-09**.

## Core judgment

If the PDF text order is broken, figures are detached from captions, or formulas are damaged, do not keep polishing prompts.
Fix the extraction backend first.

## Project-level evaluation

### Best default: Docling

Repo: https://github.com/docling-project/docling

Why it fits:

- layout-aware PDF and document conversion
- exports structured artifacts that a reading page can consume
- works as a Python-first integration target
- permissive license shape for default use

Use it as the default first pass for this skill.

### Best alternate parser: Marker

Repo: https://github.com/VikParuchuri/marker

Why it fits:

- strong PDF to Markdown / JSON / HTML conversion
- good handling of equations and images in many research PDFs
- useful when Docling still breaks badly on a specific paper

Why it is not the built-in default:

- GPL-3.0 license
- local deployment is fine, but bundling it as the default skill backend is a worse legal default than Docling

Treat it as an optional backend.

### Strong complex-document option: MinerU

Repo: https://github.com/opendatalab/MinerU

Why it fits:

- strong on complicated page layouts
- extracts to Markdown / JSON-like artifacts
- good candidate when formulas, tables, and figure-heavy pages are messy

Why it is not the built-in default:

- AGPL-3.0 license
- heavier operational footprint

Treat it as an external backend when the deployment model allows it.

### Scholarly structure add-on: GROBID

Repo: https://github.com/kermitt2/grobid

What it adds:

- title, authors, abstract
- section hierarchy
- references and citation spans
- scholarly skeleton that layout parsers sometimes flatten

Use it when bibliography, citation anchors, and section hierarchy matter.
Do not expect it to solve figure extraction or pretty math rendering by itself.

### Best figure add-on: pdffigures2

Repo: https://github.com/allenai/pdffigures2

What it adds:

- figure regions
- captions
- a true figure unit instead of whole-page screenshots or raw embedded-image dumps

Use it when figure-heavy papers need clean figure blocks.

### Formula image fallback: pix2tex / LaTeX-OCR

Repo: https://github.com/lukas-blecher/LaTeX-OCR

Use it only when equations are image-based or the main extractor destroys formula text.
Do not run OCR on clean text equations just because OCR exists.

### Rendering/UI references only: Engrafo and Lens

Repos:

- https://github.com/arxiv-vanity/engrafo
- https://github.com/elifesciences/lens

Why they matter:

- they are useful as HTML reading and article-viewer references
- they can inform page interaction, article structure, and figure/formula presentation

Why they are not the PDF backbone:

- Engrafo is centered on TeX-to-HTML workflows, not PDF reconstruction
- Lens is an article viewer, not a modern PDF extraction stack

Borrow product ideas from them.
Do not make them the extraction core.

## Recommended stack for this skill

### Immediate default

1. Docling for the main parse
2. pdfimages as a lightweight embedded-image fallback that is already available on this machine
3. KaTeX for on-page formula rendering

### Better scholarly stack

1. Docling for page body and reading order
2. GROBID for scholarly hierarchy and references
3. pdffigures2 for figure-citation pairing when figures matter heavily
4. pix2tex only for image-based formula failures

### Alternate stack when legal/deployment constraints allow it

1. Marker instead of Docling for hard PDFs
2. MinerU when pages are unusually complex and AGPL is acceptable

## Integration rule

Think in artifacts, not in one monolithic parse result.

- `docling/`: paragraph flow, headings, tables, many formulas
- `marker/` or `mineru/`: alternate page-body parse when needed
- `grobid/`: scholarly hierarchy, references, citation spans
- `figures/`: extracted figures and figure metadata
- `formula_ocr/`: only for equation-image fallback
- rendered HTML: KaTeX first, copyable LaTeX controls, optional MathJax fallback

Never annotate raw OCR fragments as if they were finished source text.
Always repair order, figure binding, and formula rendering before writing deep reading notes.

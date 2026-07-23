# Figure Reading Schema

Use this file whenever the page includes a figure in Board 1: Original Guided Reading.

The figure note should help the reader read the visual, not merely restate the caption.

## For plots and curves

Always explain:

1. what is being compared
2. what the x-axis means and which unit it uses
3. what the y-axis means and which unit it uses
4. what each curve, bar, color, or legend item stands for
5. what trend the reader should notice
6. why that trend likely appears
7. which claim in the paper this figure is actually supporting

## For spectrograms, heatmaps, and intensity maps

Always explain:

1. what each axis represents
2. what color or intensity represents
3. where the salient region is
4. whether the region indicates signal, interference, noise, or another pattern
5. what the change before and after processing means

## For architecture diagrams

Always explain:

1. the modules
2. the direction of flow
3. the input and output
4. why the architecture is arranged this way
5. which block is the real novelty and which block is standard plumbing

## For tables used as evidence

If a table is central to the argument, read it like a figure:

- what rows and columns stand for
- what metric matters most
- where the strongest result is
- what baseline or ablation matters
- whether the margin is actually meaningful

## Composite Figures (Multi-Sub-Plot Images)

Docling and most PDF extractors will extract a multi-panel figure as **one image file**.
The rendered page will display that one image, but the reading note must treat each sub-plot separately.

### How to detect

Check the OCR text associated with the figure (`picture.children` in Docling JSON, or nearby caption text).
If it contains labels like "(a) ... (b) ... (c) ..." or stacked descriptions ("BER | Array Pattern | MUSIC Spectrum"), it is composite.

### How to handle

1. Display the image once (the full composite image).
2. Write one `<details>` block **per sub-figure**, not one block for the whole image.
3. Each `<details>` block must follow the sub-plot type rules above (BER curve → x-axis/y-axis/every curve; array pattern → null depth, main lobe width, side lobe level; MUSIC spectrum → peak location, spurious peaks, resolution).
4. Name the IDs explicitly: `figure-02a-note`, `figure-02b-note`, `figure-02c-note`.
5. In `<figcaption>`, state the panel decomposition: "(a) BER / (b) Array Pattern / (c) MUSIC Spectrum".

### Common three-panel pattern in signal processing papers

Many simulation result figures contain three sub-plots per algorithm:
- **(a) BER curve** — BER vs SNR; must explain every curve in legend
- **(b) Array pattern / Beamforming pattern** — gain vs angle; explain main lobe pointing, null depth, interference direction
- **(c) MUSIC spectrum / DOA spectrum** — normalized power vs angle; explain peak positions, true DOA, interference suppression

When a section compares multiple algorithms (e.g. MVDR, LCMV, GSC, PI, SD), each algorithm typically gets its own three-panel figure.
Write three separate `<details>` for each, totaling 3 × N blocks for N algorithms.

### Do not

- Do not write a single generic `<details>` that covers all sub-plots with one paragraph.
- Do not repeat the same "对照 PDF 确认" placeholder.
- Do not omit sub-plot (b) or (c) because only (a) was mentioned in the surrounding text.

## Style

Stay concrete.
If the paper gives a figure, the reading note should help the user see the figure, not just hear a summary of it.

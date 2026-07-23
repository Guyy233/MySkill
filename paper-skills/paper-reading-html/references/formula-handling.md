# Formula Handling

Use this file when the source contains formulas.

The rule is simple: show the math, then explain the math.

## Rendering

Keep displayed formulas visible in the source column.
Prefer **KaTeX** for page rendering because it is faster and more stable for reading pages.
Use **MathJax** only when the page needs TeX features or macros that KaTeX cannot render cleanly.
Expose a one-click way to copy the LaTeX source without making raw LaTeX the default visual form.

### KaTeX `data-latex` attribute encoding (critical)

When embedding LaTeX in an HTML attribute for client-side KaTeX rendering, the attribute value **must** use actual double-quote delimiters, not HTML entity `&quot;`:

```html
<!-- CORRECT: JS getAttribute() returns the full LaTeX string -->
<div class='katex-block' data-latex="E = mc^2" style='display:none;'>

<!-- WRONG: JS getAttribute() receives a truncated/broken string -->
<div class="katex-block" data-latex=&quot;E = mc^2&quot; style="display:none;">
```

If `data-latex=&quot;` appears in the generated HTML, **all formulas will silently fail** — the fallback image is shown instead and no KaTeX error is printed.
Fix: use single-quoted Python f-strings for the outer HTML, actual `"` for the attribute value, and escape any internal `"` inside the LaTeX as `&quot;`.

### `sanitize_for_katex()` regex safety

When cleaning OCR-extracted LaTeX with `re.sub()`, the replacement string must not contain `\c`, `\m`, or other sequences that Python interprets as bad regex escapes.
Use raw strings `r'\1'` or plain `.replace()` instead of `re.sub()` replacements for any substitution that touches backslash characters.

## Reconstruction

When PDF extraction damages equation layout:

- rebuild conservatively
- keep original notation whenever possible
- do not invent missing symbols unless the source context makes the reconstruction clear
- if uncertainty remains, mark the formula as approximate reconstruction

## Formula note structure

For each important formula, explain:

1. what this formula is doing
2. what each key variable means
3. how it connects to the previous and next method step
4. whether it is a definition, constraint, objective, or update rule
5. what the reader misses if this formula is skipped

## Optimization formulas

If the formula is an optimization problem, explicitly say:

- what is being optimized
- under which constraints
- what the tradeoff means

## Matrix and signal-processing formulas

For array processing, beamforming, estimation, filtering, and time-frequency papers, name the role of:

- steering vectors
- covariance matrices
- weight vectors
- constraints
- eigenstructure or subspace terms

Do not assume the reader will infer these roles from notation alone.

## Per-symbol explanations via SYMBOL_DICT

For domain-specific papers, maintain a `SYMBOL_DICT` that maps LaTeX tokens to Chinese (or target-language) explanations.
This is more reliable than keyword-based context matching, which produces placeholder text when the surrounding text does not contain the right keywords.

```python
SYMBOL_DICT: dict[str, str] = {
    r'\mathbf{x}': '**阵列接收信号矢量** x(n)，N×1 复向量，N 为阵元数。',
    r'\mathbf{w}': '**波束形成权重向量** w，N×1，决定阵列的空间指向性。',
    r'\mathbf{R}': '**协方差矩阵** R = E[x(n)xᴴ(n)]，N×N Hermitian 正定矩阵。',
    # ... one entry per distinct symbol in the domain
}
```

When extracting symbols from a formula:
1. Iterate `SYMBOL_DICT` from longest token to shortest (avoids partial matches).
2. Skip duplicate base symbols (`\mathbf{w}` and `w` both map to "权重向量" — keep only the first hit).
3. If no SYMBOL_DICT entry matches any token in the formula, fall back to a minimal context note — never output generic placeholder paragraphs like "建议对照 PDF 原文确认变量定义...".

## Python string hygiene when writing HTML

When building multi-line HTML strings in Python:

- Do **not** use ASCII `"` inside a double-quoted Python string. It terminates the string silently.
- Use `【】` or `『』` for Chinese quotation marks inside HTML content strings.
- Prefer single-quoted Python strings `'...'` for outer delimiters when the content contains `"`.
- When writing a long HTML block, use string concatenation `("part1" "part2" ...)` rather than triple-quoted heredocs if the content may contain any ASCII `"` or smart-quote characters.

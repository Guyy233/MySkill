---
name: paper-reading-html
description: Build reading-oriented HTML pages from academic papers, PDFs, or extracted manuscript text. Use when the goal is close reading: keep the paper visible in reading order, render formulas and figures on the page, add paragraph-by-paragraph guided reading, optionally add a Chinese translation column for mainly English source text, and preserve a separate whole-paper interpretation board.
---

# Paper Reading HTML

## What This Skill Is For

Use this skill when the user wants **论文网页化 + 全文带读 + 全文解读**。
它的目标不是做海报页，也不是做一屏摘要页。
它要做的是：
先把论文按原始阅读顺序重建出来，再在网页上把段落、图和公式一点点讲清楚。

## Default Output Shape

页面固定保留两个板块，而且顺序固定。

前半部分是 **文档解读**。
它先把全文主线、方法链、证据链、限制条件和应记住的结论立住。

后半部分是 **原文带读**。
它按论文真实顺序保留原文段落、图片、公式和图表，再给每一段、每一张图、每一处关键公式配上带读说明。

不要把这两个板块混成一个摘要页。
不要只写提纲，不重建原文。

## Non-Negotiable Rule

如果原文顺序错了、图片脱节了、公式看不清，就不要继续修 prompt 词藻。
先修抽取和渲染链。

## Known Bugs Fixed (Record for Re-runs)

以下是上线后发现并已修复的渲染 bug，重建页面前先确认这些修复仍在代码里：

### Bug 1 — KaTeX `data-latex` 属性编码错误（已修复）

**现象**：所有公式显示为截图回退，网页里 KaTeX 不渲染任何公式。
**根因**：`render_formula_block()` 写出的是 `data-latex=&quot;...&quot;`，HTML 解析器不把 `&quot;` 当属性界定符，JS 的 `getAttribute('data-latex')` 返回截断或错误值。
**修复**：改为 `data-latex="..."` 使用真正的双引号作为属性界定符，内部的 `"` 用 `&quot;` HTML 转义。代码见 `render_formula_block()` 中 `katex_rendered` 构造处。

### Bug 2 — `sanitize_for_katex()` 中 regex 替换字符串含 `\c`/`\m` 等非法转义

**现象**：脚本在某些公式上抛出 `re.PatternError: bad escape`。
**修复**：替换字符串改用 raw string `r'\...'` 或 `.replace()` 而非 `re.sub()` 的 replacement 字符串。

### Bug 3 — Python 源码中中文引号 `"..."` 导致 SyntaxError

**现象**：脚本文件用双引号 `"` 作为 Python string delimiter，如果 HTML 内容里也含有 ASCII `"` 字符（如 `验证"GSC 与 LCMV 等效"` 这种写法），会截断 Python string。
**规范**：HTML 字符串内用 `【】` 或 `『』` 代替中文引号，或改用单引号 Python string（`'...'`）；永远不在双引号 Python string 内直接写未转义的 ASCII `"`。

## Running Requirements

**必须从项目根目录运行**，否则中文路径会因工作目录不同而乱码：

```bash
cd D:\study\A_finalyear_prj
python -B MySkill_repo/paper-reading-html/scripts/build_paper_reading_html.py repro
```

`-B` 参数禁用 `.pyc` 缓存，避免修改脚本后旧缓存仍然生效。

## Main Entry Script

统一入口是 `scripts/build_paper_reading_html.py`。
它现在有五条主路径：

- `python scripts/build_paper_reading_html.py extract <pdf> --out-dir <dir>`
  先做结构化抽取，保留 Docling 等产物。

- `python scripts/build_paper_reading_html.py render-docling --extract-dir <dir> --out-dir <dir> [--pdf <pdf>]`
  直接把已有的 Docling 抽取结果渲染成 **全文带读网页**。

- `python scripts/build_paper_reading_html.py from-pdf <pdf> --extract-dir <dir> --out-dir <dir>`
  从 PDF 一步生成 **抽取结果 + 全文带读网页**。以后做新论文，默认先用这条。

- `python scripts/build_paper_reading_html.py repro`
  重建 repro 三篇论文网页。其中第二、第三篇会走新的 **Docling 全文带读渲染器**，第一篇再用专门的深度模板覆盖回去。

- `python scripts/build_paper_reading_html.py first-paper`
  单独重跑第一篇深度版。

## Script Roles

### `scripts/extract_pdf_pipeline.py`

负责抽取 PDF，产出 Docling / Marker / pdfimages 一类结构化中间产物。
它是抽取层，不负责最后网页质量。

### `scripts/render_docling_guided_html.py`

这是现在的 **通用全文带读渲染器**。
它直接吃 Docling JSON，不再只靠 markdown 占位符拼页面。

它会做几件关键事：

- 按 Docling 的真实顺序恢复章节、段落、列表、图片、公式
- 从整页栅格图中裁出 **图片块**，保持原文版面位置
- 从整页栅格图中裁出 **公式块**，先保证网页里能读
- 给段落、图片、公式各自生成带读卡片
- 给术语加点击解释
- 在页面前部补一层文档解读板块

以后要把一篇论文稳定做成“全文提取再带读分析”，默认就是修这个脚本，不是再为单篇特判。

### `scripts/build_first_paper_rerun.py`

这是第一篇的专用深度模板。
它目前仍然是样例里最细的一版，所以 repro 重建后会再用它覆盖第一篇。

### `scripts/rebuild_repro_reading_pages.py`

它负责 repro 样例站点的基础索引和框架页。
但第二、第三篇正文页面现在已经不靠它的旧简化模板，而是交给 `render_docling_guided_html.py` 重建。

## Reading Workflow

### 1. 先恢复原文顺序

先对齐章节、段落、图、公式，再开始解释。
不要把 OCR 噪声当正文。
不要把图内字符碎片当独立段落。

### 2. 再建立文档解读板块

先回答整篇文章在解决什么、靠什么方法推进、用什么证据站住。
这一层帮助读者先把地图看明白。

### 3. 再做原文带读板块

每个重要段落都要有对应带读卡片。
每张关键图都要有图解卡片。
每处关键公式至少要做到 **网页里可见**，并在可能时补上可复制公式文本。

### 4. 图和公式优先保证可读

**图**：不要只给一句话。每张图的展开图解必须覆盖：

- 图形类型（BER曲线 / 方向图 / MUSIC谱 / 结构框图 / 几何图）
- 横轴含义与单位
- 纵轴含义与单位
- 每条曲线或每个标注的具体含义
- 关键趋势（哪里分叉、哪里收敛、零陷深度等）
- 趋势背后的物理原因
- 这张图支持了哪个具体结论

**合成图（多子图在一张图里）**：Docling 有时把多个子图提取为一张图片（如三联结果图：BER + 方向图 + MUSIC谱）。遇到这种情况必须：

1. 识别出子图数量（通常看 OCR 提取的标注文字）
2. 为每个子图单独写一个 `<details>` 展开块
3. 各子图 `id` 格式：`figure-02a-note`、`figure-02b-note`、`figure-02c-note`
4. 如果多张图共属同一个"三联组"（如 MVDR/LCMV/GSC/PI/SD 各自的 BER+方向图+MUSIC 谱），在 `<figcaption>` 里明确说明子图划分

**公式**：不要只给 LaTeX 代码。
优先保证网页里先能看，再考虑复制文本或 LaTeX。
当前通用路径是：

- 先从页图裁出公式块
- 再在可行时补可复制公式文本
- 公式展开里必须对每个字母/符号单独解释（利用 `SYMBOL_DICT` + `derive_formula_symbols()`）

### 5. 最后检查页面有没有真的帮助阅读

完成前至少确认：

- 原文顺序没有乱
- 图和对应文字没有脱节
- 公式在网页里可见
- 带读卡片不是空泛复述
- 文档解读和原文带读没有互相矛盾

## Output Style Rules

页面是阅读空间，不是宣传页。
前面先给文档解读，后面再给原文带读。
要让读者能够顺着网页把整篇文章读通，而不是只看几个卡片标题。

如果用户额外要求英文论文加中文翻译列，可以在这个基础上再扩中间列；但默认先把 **原文重建 + 带读分析** 这条主链做稳。

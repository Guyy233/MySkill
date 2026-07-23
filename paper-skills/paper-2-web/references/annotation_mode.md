# Annotation-First Paper2Web Mode

## Purpose

This mode is for **study-oriented paper webpages**, not promotional homepages.
It is the right choice when the user wants:

- the **original paper text** preserved in the webpage
- a **side-by-side explanation**
- a **Chinese translation column** inserted when the source is mainly English
- **formulas rewritten in LaTeX** and rendered readably on the page
- **clickable professional terms** that show definitions

## Required Output Structure

The default output is still a single `index.html` per paper, but the content structure changes:

1. **Sticky top navigation**
   - paper title
   - course / project info
   - mode badge: `Prompt A` or `Prompt B`

2. **Sticky chapter rail**
   - jump to sections
   - visible reading progress

3. **Main annotation body**
   - left column: original text
   - middle column: Chinese translation, only when the source is mostly English
   - right column: explanation and logic unpacking

4. **Formula rendering**
   - if the PDF / LaTeX source contains formulas, rewrite them to valid LaTeX
   - render with MathJax or KaTeX
   - do not leave raw OCR fragments as unreadable math garbage

5. **Terminology interaction**
   - important terms should be clickable
   - click opens a tooltip, drawer, or floating panel with a short explanation

6. **Bottom worksheet / summary**
   - one-line thesis
   - strongest evidence
   - method map
   - limits / possible objections

## Two Prompt Directions

### Prompt A

Use this when the user already has a set of questions and wants the page to answer them.

The right-column explanation should emphasize:

- what this paragraph is doing
- which question it answers
- whether the evidence is enough
- what is still missing

### Prompt B

Use this when the user wants pure logical unpacking without preset questions.

The right-column explanation should emphasize:

- paragraph function
- logical role in the whole paper
- strongest claim or method in that paragraph
- hidden assumptions, weaknesses, or limits

## Formula Rules

- Prefer formulas recovered from the source itself.
- When OCR is noisy, reconstruct the formula carefully instead of copying broken symbols.
- If exact recovery is impossible, state the formula as a **core equivalent form** and say so.
- For methods like MUSIC, MVDR, LCMV, GSC, PI, CME, FCME, prefer standard readable notation.

## Quality Bar

The page is not complete unless it satisfies all of the following:

- the original text is still visible
- the explanation is paragraph-aligned, not only document-level summary
- formulas are readable
- important terms can be clicked for explanation
- mobile layout collapses cleanly
- the page still works as a local HTML preview

## 双层阅读模式

批注式网页现在默认支持两层同时保留：

- **整篇原文解读**：先交代整篇论文的主张、证据、方法链、边界
- **全文带读**：再按段进入原文、翻译、带读解释

这两层不是二选一，而是同时存在。

## 图片处理规则

如果论文原文中存在图片、流程图、实验图、曲线图：

- 图片要放在 **原文栏** 对应位置附近
- 带读栏要同步补上 **图像解读**
- 图像解读至少包括：
  - 图里有什么
  - x 轴 / y 轴 或关键变量
  - 曲线或图形趋势
  - 为什么会出现这个趋势
  - 这个图最终说明什么




## 新版结构补充

如果用户明确要求“原文带读”和“文档解读”同时存在，则页面必须拆成 **两个独立板块**：

- **板块一：原文带读**
  - 第一栏放原文
  - 若原文主要是英文，中间加中文翻译栏
  - 图片、公式、表格优先回到原文栏
  - 右侧带读栏逐段做批注和解释

- **板块二：文档解读**
  - 单独压缩整篇逻辑
  - 提炼主张、证据、方法链、章节逻辑和边界
  - 这一板块才对应 Prompt A / Prompt B 的整篇解读诉求

### 图片补充规则

- 如果 PDF 中图片是独立嵌入资源，优先直接抽取原图，而不是用整页截图代替
- 如果只能拿到页图，再退回页图方案

### 公式补充规则

- 公式首先属于 **原文带读板块** 的原文栏
- 原文栏里的公式要以 LaTeX 可读形式展示
- 带读栏负责解释公式在这一段里的作用，而不是把公式藏到解释栏里

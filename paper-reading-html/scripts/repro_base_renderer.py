from __future__ import annotations

import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(r"D:\study\A_finalyear_prj")
REPRO_DIR = ROOT / "结题" / "document" / "repro"
OUTPUT_DIR = REPRO_DIR / "paper2web"
ASSETS_DIR = OUTPUT_DIR / "assets"
PREVIEW_DIR = ASSETS_DIR / "previews"
FIGURE_DIR = ASSETS_DIR / "figures"
FIGURE_MAP: dict[tuple[str, str, int], list[dict]] = {}


def pick_command(*candidates: str) -> str | None:
    for candidate in candidates:
        if not candidate:
            continue
        direct = shutil.which(candidate)
        if direct:
            return direct
        path = Path(candidate)
        if path.exists():
            return str(path)
    return None


PDFTOPPM = pick_command(
    "pdftoppm",
    r"D:\Appstore\LaTex\App\texlive\2025\bin\windows\pdftoppm.exe",
)
PDFIMAGES = pick_command(
    "pdfimages",
    r"D:\Appstore\LaTex\App\texlive\2025\bin\windows\pdfimages.exe",
)


STYLE = r"""
:root {
  --ink: #16313b;
  --muted: #5f7380;
  --line: rgba(22, 49, 59, 0.14);
  --paper: #f7f4ea;
  --panel: rgba(255,255,255,0.88);
  --panel-strong: #ffffff;
  --accent: #0d6e7e;
  --accent-soft: rgba(13, 110, 126, 0.12);
  --mark: #fff1a8;
  --shadow: 0 18px 40px rgba(22, 49, 59, 0.08);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(13,110,126,0.12), transparent 32%),
    radial-gradient(circle at top right, rgba(215,155,63,0.12), transparent 24%),
    linear-gradient(180deg, #f9f6ef 0%, #f0ece1 100%);
  font: 16px/1.7 "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
}
a { color: inherit; }
.top-nav {
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(16px);
  background: rgba(247,244,234,0.82);
  border-bottom: 1px solid var(--line);
}
.top-nav-inner, .hero-panel, .content-shell, .home-shell {
  width: min(1440px, calc(100vw - 32px));
  margin: 0 auto;
}
.top-nav-inner {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
}
.nav-brand { text-decoration: none; font-weight: 700; }
.nav-meta { display: flex; gap: 12px; flex-wrap: wrap; color: var(--muted); font-size: 14px; }
.nav-link { text-decoration: none; color: var(--accent); }
.annot-shell, .home-shell { padding: 28px 0 40px; }
.hero-panel {
  display: grid;
  grid-template-columns: 1.6fr minmax(240px, 0.9fr);
  gap: 24px;
  align-items: stretch;
  padding: 12px 0 28px;
}
.hero-copy, .hero-preview, .toc-card, .board-panel, .home-card, .note-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 24px;
  box-shadow: var(--shadow);
}
.hero-copy { padding: 28px; }
.hero-kicker, .eyebrow, .section-kicker, .panel-kicker {
  margin: 0 0 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
  color: var(--muted);
}
.hero-copy h1, .board-head h2, .chapter-head h3, .home-card h2 {
  margin: 0;
  line-height: 1.15;
}
.hero-abstract, .chapter-summary, .worksheet-body, .analysis-body, .term-panel-body { color: var(--ink); }
.legend-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 18px; }
.legend-chip, .mode-pill, .glossary-chip, .term-btn, .copy-btn {
  border: 1px solid var(--line);
  background: var(--panel-strong);
  border-radius: 999px;
  padding: 8px 12px;
  font: inherit;
}
.mode-pill { background: var(--accent-soft); color: var(--accent); font-weight: 700; }
.hero-preview { padding: 14px; display: flex; align-items: center; justify-content: center; }
.hero-preview img, .source-figure img, .home-card img {
  width: 100%;
  height: auto;
  border-radius: 18px;
  border: 1px solid var(--line);
  object-fit: cover;
}
.content-shell {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}
.toc-rail { position: sticky; top: 88px; display: grid; gap: 16px; }
.toc-card { padding: 18px; }
.toc-links { display: grid; gap: 10px; }
.toc-link {
  display: grid;
  grid-template-columns: 44px 1fr;
  gap: 10px;
  align-items: start;
  text-decoration: none;
}
.toc-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 700;
}
.board-panel { padding: 22px; margin-bottom: 22px; }
.board-head { margin-bottom: 16px; }
.board-stack { display: grid; gap: 18px; }
.chapter-block {
  border: 1px solid var(--line);
  border-radius: 22px;
  background: rgba(255,255,255,0.68);
  overflow: hidden;
}
.chapter-head {
  display: grid;
  grid-template-columns: 84px 1fr;
  gap: 18px;
  padding: 18px 18px 12px;
  border-bottom: 1px solid var(--line);
}
.chapter-index {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 72px;
  border-radius: 18px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 24px;
  font-weight: 800;
}
.annot-row {
  display: grid;
  gap: 16px;
  padding: 16px 18px 18px;
  border-top: 1px solid rgba(22,49,59,0.08);
}
.annot-row.cols-2 { grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr); }
.annot-row.cols-3 { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr); }
.annot-col {
  min-width: 0;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(255,255,255,0.78);
}
.col-head {
  margin-bottom: 12px;
  color: var(--muted);
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.prose p, .figure-read p, .analysis-item, .formula-note, .worksheet-body p { margin: 0 0 12px; }
.prose p:last-child, .formula-note:last-child, .analysis-item:last-child { margin-bottom: 0; }
.analysis-stack, .worksheet-grid, .map-grid, .glossary-flow, .media-stack, .figure-gallery, .figure-read-stack, .home-grid {
  display: grid;
  gap: 12px;
}
.analysis-item {
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(13,110,126,0.06);
  border: 1px solid rgba(13,110,126,0.08);
}
.analysis-label, .worksheet-label, .figure-read-caption, .formula-caption {
  margin: 0 0 6px;
  font-weight: 700;
}
.formula-block {
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.92);
}
.formula-head {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.formula-display { overflow-x: auto; }
.source-figure, .home-card figure { margin: 0; }
.source-figure figcaption { margin-top: 8px; color: var(--muted); font-size: 14px; }
mark {
  background: linear-gradient(180deg, transparent 35%, var(--mark) 35% 100%);
  padding: 0 2px;
}
.worksheet-grid, .map-grid, .home-grid {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}
.worksheet-card, .map-card, .home-card {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.82);
}
.home-card { display: grid; gap: 14px; }
.home-card a {
  display: inline-flex;
  width: fit-content;
  text-decoration: none;
  color: var(--accent);
  font-weight: 700;
}
.term-panel {
  position: fixed;
  right: 16px;
  bottom: 16px;
  width: min(360px, calc(100vw - 32px));
  padding: 18px;
  border-radius: 22px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.96);
  box-shadow: var(--shadow);
}
.term-close {
  position: absolute;
  right: 12px;
  top: 12px;
  border: 0;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
}
@media (max-width: 1180px) {
  .content-shell { grid-template-columns: 1fr; }
  .toc-rail { position: static; }
  .annot-row.cols-2, .annot-row.cols-3, .hero-panel { grid-template-columns: 1fr; }
}
@media (max-width: 720px) {
  .top-nav-inner, .hero-panel, .content-shell, .home-shell { width: min(100vw - 20px, 1440px); }
  .chapter-head { grid-template-columns: 1fr; }
  .chapter-index { min-height: 54px; }
}
"""

SCRIPT = r"""
document.addEventListener('click', (event) => {
  const term = event.target.closest('.term-btn');
  if (term) {
    const panel = document.getElementById('term-panel');
    panel.hidden = false;
    panel.querySelector('.term-panel-title').textContent = term.dataset.term || '术语';
    panel.querySelector('.term-panel-body').textContent = term.dataset.definition || '暂无说明。';
    return;
  }
  const copy = event.target.closest('.copy-btn');
  if (copy) {
    navigator.clipboard.writeText(copy.dataset.latex || '').then(() => {
      const old = copy.textContent;
      copy.textContent = '已复制';
      setTimeout(() => copy.textContent = old, 1200);
    });
    return;
  }
  const close = event.target.closest('.term-close');
  if (close) {
    document.getElementById('term-panel').hidden = true;
  }
});
"""


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def esc_attr(text: str) -> str:
    return html.escape(text, quote=True)


def rich(text: str, glossary: dict[str, str]) -> str:
    s = html.escape(text)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\{\{(.+?)\}\}", r"<mark>\1</mark>", s)

    def term(match: re.Match[str]) -> str:
        word = html.unescape(match.group(1))
        meaning = glossary.get(word, "")
        return f"<button type='button' class='term-btn' data-term='{esc_attr(word)}' data-definition='{esc_attr(meaning)}'>{html.escape(word)}</button>"

    return re.sub(r"\[\[(.+?)\]\]", term, s)


def paras(items: list[str], glossary: dict[str, str]) -> str:
    return ''.join(f"<p>{rich(item, glossary)}</p>" for item in items)


def formula_html(item: dict[str, str], glossary: dict[str, str]) -> str:
    note = f"<p class='formula-note'>{rich(item.get('note', ''), glossary)}</p>" if item.get('note') else ''
    return (
        "<div class='formula-block'>"
        "<div class='formula-head'>"
        f"<div class='formula-caption'>{html.escape(item['caption'])}</div>"
        f"<button type='button' class='copy-btn' data-latex='{esc_attr(item['latex'])}'>复制 LaTeX</button>"
        "</div>"
        f"<div class='formula-display'>\\[{html.escape(item['latex'])}\\]</div>"
        f"{note}</div>"
    )


def analysis_html(items: dict[str, str], glossary: dict[str, str]) -> str:
    return ''.join(
        "<div class='analysis-item'>"
        f"<div class='analysis-label'>{html.escape(label)}</div>"
        f"<div class='analysis-body'>{rich(body, glossary)}</div>"
        "</div>"
        for label, body in items.items()
    )


def ensure_preview(slug: str, pdf_path: Path) -> str | None:
    if not PDFTOPPM:
        return None
    ensure_dir(PREVIEW_DIR)
    preview = PREVIEW_DIR / f"{slug}-01.png"
    if preview.exists():
        return f"../assets/previews/{preview.name}"
    prefix = PREVIEW_DIR / slug
    run([PDFTOPPM, '-f', '1', '-l', '1', '-png', str(pdf_path), str(prefix)])
    for candidate in (PREVIEW_DIR / f"{slug}-01.png", PREVIEW_DIR / f"{slug}-1.png"):
        if candidate.exists():
            if candidate.name != preview.name:
                candidate.replace(preview)
            return f"../assets/previews/{preview.name}"
    return None


def ensure_embedded_figures(slug: str, pdf_path: Path, page: int) -> list[str]:
    if not PDFIMAGES:
        return []
    target_dir = ensure_dir(FIGURE_DIR / slug / f"p{page:02d}")
    if any(target_dir.iterdir()):
        return [f"../assets/figures/{slug}/p{page:02d}/{item.name}" for item in sorted(target_dir.iterdir()) if item.is_file()]
    stage = ensure_dir(Path(tempfile.gettempdir()) / 'paper-reading-html' / slug / f'p{page:02d}')
    prefix = stage / 'img'
    run([PDFIMAGES, '-f', str(page), '-l', str(page), '-all', str(pdf_path), str(prefix)])
    rels: list[str] = []
    for item in sorted(stage.glob('img-*.*')):
        dest = target_dir / item.name
        shutil.copy2(item, dest)
        rels.append(f"../assets/figures/{slug}/p{page:02d}/{dest.name}")
    return rels


def figure_gallery(paper_slug: str, paper_pdf: Path, chapter_id: str, row_index: int, glossary: dict[str, str]) -> str:
    figures = FIGURE_MAP.get((paper_slug, chapter_id, row_index), [])
    if not figures:
        return ''
    blocks = []
    for item in figures:
        images = ensure_embedded_figures(paper_slug, paper_pdf, item['page'])
        for idx, rel in enumerate(images or [''], 1):
            if not rel:
                continue
            caption = item['caption'] if len(images) == 1 else f"{item['caption']} · 图块 {idx}"
            blocks.append(
                "<figure class='source-figure'>"
                f"<img src='{rel}' alt='{esc_attr(caption)}'>"
                f"<figcaption>{rich(caption, glossary)}</figcaption>"
                "</figure>"
            )
    return f"<div class='figure-gallery'>{''.join(blocks)}</div>" if blocks else ''


def figure_read_stack(paper_slug: str, chapter_id: str, row_index: int, glossary: dict[str, str]) -> str:
    figures = FIGURE_MAP.get((paper_slug, chapter_id, row_index), [])
    if not figures:
        return ''
    cards = []
    for item in figures:
        cards.append(
            "<div class='analysis-item'>"
            f"<div class='analysis-label'>{rich(item['caption'], glossary)}</div>"
            f"<div class='analysis-body'>{analysis_html(item['analysis'], glossary)}</div>"
            "</div>"
        )
    return f"<div class='figure-read-stack'><div class='col-head'>图像带读</div>{''.join(cards)}</div>"


def row_html(row: dict, glossary: dict[str, str], paper_slug: str, paper_pdf: Path, chapter_id: str, row_index: int) -> str:
    has_translation = bool(row.get('translation'))
    cls = 'cols-3' if has_translation else 'cols-2'
    cols = [
        "<div class='annot-col'>"
        "<div class='col-head'>原文</div>"
        f"<div class='prose'>{paras(row['original'], glossary)}</div>"
        f"<div class='media-stack'>{''.join(formula_html(item, glossary) for item in row.get('formulas', []))}{figure_gallery(paper_slug, paper_pdf, chapter_id, row_index, glossary)}</div>"
        "</div>"
    ]
    if has_translation:
        cols.append(
            "<div class='annot-col'>"
            "<div class='col-head'>翻译</div>"
            f"<div class='prose'>{paras(row['translation'], glossary)}</div>"
            "</div>"
        )
    cols.append(
        "<div class='annot-col'>"
        "<div class='col-head'>带读</div>"
        f"<div class='analysis-stack'>{analysis_html(row['analysis'], glossary)}</div>"
        f"{figure_read_stack(paper_slug, chapter_id, row_index, glossary)}"
        "</div>"
    )
    return f"<div class='annot-row {cls}'>{''.join(cols)}</div>"


def toc(chapters: list[dict]) -> str:
    items = [
        "<a href='#guided-reading' class='toc-link'><span class='toc-index'>A</span><span>原文带读</span></a>",
        "<a href='#document-reading' class='toc-link'><span class='toc-index'>B</span><span>文档解读</span></a>",
    ]
    for chapter in chapters:
        items.append(f"<a href='#{chapter['id']}' class='toc-link'><span class='toc-index'>{html.escape(chapter['index'])}</span><span>{html.escape(chapter['title'])}</span></a>")
    return ''.join(items)


def chapter_map(chapters: list[dict], glossary: dict[str, str]) -> str:
    return ''.join(
        "<article class='map-card'>"
        f"<p class='worksheet-label'>{html.escape(chapter['index'])} · {html.escape(chapter['title'])}</p>"
        f"<div class='worksheet-body'>{rich(chapter['summary'], glossary)}</div>"
        "</article>"
        for chapter in chapters
    )


def overview_cards(cards: list[dict], glossary: dict[str, str]) -> str:
    return ''.join(
        "<article class='worksheet-card'>"
        f"<p class='worksheet-label'>{html.escape(card['label'])}</p>"
        f"<div class='worksheet-body'>{rich(card['body'], glossary)}</div>"
        "</article>"
        for card in cards
    )


def shell(title: str, body: str) -> str:
    return f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{html.escape(title)}</title><style>{STYLE}</style><script>window.MathJax={{tex:{{inlineMath:[[\\'\\(\\',\\'\\)\\']],displayMath:[[\\'\\[\\',\\'\\]\\']]}},options:{{skipHtmlTags:[\\'script\\',\\'noscript\\',\\'style\\',\\'textarea\\',\\'pre\\']}}}};</script><script defer src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js'></script><script defer>{SCRIPT}</script></head><body>{body}<aside id='term-panel' class='term-panel' hidden><button type='button' class='term-close' aria-label='关闭'>×</button><p class='panel-kicker'>术语解释</p><h3 class='term-panel-title'>术语</h3><p class='term-panel-body'></p></aside></body></html>"


def page(paper: dict, preview_name: str | None) -> str:
    glossary = paper['glossary']
    preview = f"<div class='hero-preview'><img src='{preview_name}' alt='{esc_attr(paper['title'])} 首页预览'></div>" if preview_name else ""
    sections = []
    for chapter in paper['chapters']:
        rows = ''.join(row_html(row, glossary, paper['slug'], paper['pdf'], chapter['id'], idx) for idx, row in enumerate(chapter['rows']))
        sections.append(
            f"<section id='{chapter['id']}' class='chapter-block'><div class='chapter-head'><div class='chapter-index'>{html.escape(chapter['index'])}</div><div><p class='eyebrow'>{html.escape(chapter['strap'])}</p><h3>{html.escape(chapter['title'])}</h3><p class='chapter-summary'>{rich(chapter['summary'], glossary)}</p></div></div>{rows}</section>"
        )
    body = (
        "<header class='top-nav'><div class='top-nav-inner'>"
        "<a href='../index.html' class='nav-brand'>Paper Reading HTML</a>"
        f"<div class='nav-meta'><span>{html.escape(paper['title'])}</span><span>{html.escape(paper.get('course', ''))}</span><a class='nav-link' href='../../{html.escape(paper['pdf'].name)}'>原 PDF</a></div>"
        "</div></header>"
        "<main class='annot-shell'>"
        f"<section class='hero-panel'><div class='hero-copy'><p class='hero-kicker'>{html.escape(paper.get('hero_kicker', 'paper-reading-html · 精读模式'))}</p><h1>{html.escape(paper['title'])}</h1><p class='hero-abstract'>{rich(paper.get('hero_abstract', ''), glossary)}</p></div>{preview}</section>"
        "<div class='content-shell'><aside class='toc-rail'><div class='toc-card'><p class='eyebrow'>章节导航</p><nav class='toc-links'>"
        f"{toc(paper['chapters'])}</nav></div><div class='toc-card'><p class='eyebrow'>术语点击解释</p><div class='glossary-flow'>"
        f"{''.join(f'<button type=\'button\' class=\'glossary-chip term-btn\' data-term=\'{esc_attr(term)}\' data-definition=\'{esc_attr(defn)}\'>{html.escape(term)}</button>' for term, defn in paper['glossary'].items())}</div></div></aside>"
        "<section class='main-flow'><section id='guided-reading' class='board-panel'><div class='board-head'><p class='eyebrow'>Board 1</p><h2>原文带读</h2><p class='chapter-summary'>按论文阅读顺序保留原文、公式、图像和局部证据，再在旁边逐段解释这一段到底在做什么。</p></div><div class='board-stack'>"
        f"{''.join(sections)}</div></section>"
        "<section id='document-reading' class='board-panel'><div class='board-head'><p class='eyebrow'>Board 2</p><h2>文档解读</h2><p class='chapter-summary'>退后一步，把整篇文章压成 thesis、方法链、证据链、边界和最后应当记住的判断。</p></div>"
        f"<div class='worksheet-grid'>{overview_cards(paper.get('overview_cards', paper.get('worksheet_cards', [])), glossary)}</div><div class='board-head' style='margin-top:18px'><h2>章节逻辑地图</h2><p class='chapter-summary'>不重复标题，而是说明每一节在整篇论证中承担什么角色。</p></div><div class='map-grid'>{chapter_map(paper['chapters'], glossary)}</div></section></section></div></main>"
    )
    return shell(f"{paper['title']} | Paper Reading HTML", body)


def home(cards: str) -> str:
    body = (
        "<main class='home-shell'><section class='hero-copy'><p class='hero-kicker'>paper-reading-html · 精读模式</p><h1>论文网页化入口</h1><p class='hero-abstract'>这里收的是精读型网页，不是展示型主页。每篇页面都包含原文带读和整篇文档解读两块。</p></section><section class='home-grid'>"
        f"{cards}</section></main>"
    )
    return shell('Paper Reading HTML', body)


PAPERS = [
    {
        'slug': 'time-frequency-interference',
        'title': '时频域干扰抑制算法',
        'pdf': REPRO_DIR / '时频域干扰抑制算法.pdf',
        'theme': 'teal',
        'course': '结题 / repro / paper-reading-html',
        'hero_kicker': 'paper-reading-html · 精读模式',
        'hero_abstract': '先把基带抗干扰拆成频域和时域两条链，再分别看检测、抑制和 BER 收口。',
        'glossary': {
            'CME': 'Consecutive Mean Excision。先估背景，再剔除高能异常点。',
            'FCME': 'Forward CME。先排序再扩展背景集合。',
            'FFT': '快速傅里叶变换，把时域数据变到频域。',
            'BER': 'Bit Error Rate，误码率。',
            'OFDM': '正交频分复用。',
            '置零': '把已判为受干扰的频点或样点直接设为 0。',
            '占空比': '一个干扰周期内，干扰持续时间占整个周期的比例。',
        },
        'worksheet_cards': [],
        'chapters': [
            {'id': 'overview', 'index': '01', 'strap': '总览', 'title': '先把问题拆成频域和时域两条链', 'summary': '全文先分域，再分别谈检测、抑制和性能。', 'rows': []},
            {'id': 'freq-detect', 'index': '02', 'strap': '频域检测', 'title': '频域路线先解决看清和门限', 'summary': '先加窗稳频谱，再比较 [[CME]] 与 [[FCME]]，最后处理平滑和漏检。', 'rows': []},
            {'id': 'freq-suppress', 'index': '03', 'strap': '频域抑制', 'title': '频域抑制真正执行的是置零', 'summary': '把检测集合变成切除动作，再看单音和窄带场景里副作用如何抬头。', 'rows': []},
            {'id': 'time-detect', 'index': '04', 'strap': '时域检测', 'title': '时域检测围着脉冲结构展开', 'summary': '高斯脉冲干扰在时域更显眼，重点变量换成周期、持续时间和占空比。', 'rows': []},
            {'id': 'time-suppress', 'index': '05', 'strap': '时域抑制', 'title': '时域置零要和占空比一起看代价', 'summary': '时域置零能切掉脉冲，但也会挖掉原始样点，所以最后还得回到 [[BER]]。', 'rows': []},
        ],
    },
    {
        'slug': 'spatial-anti-jamming',
        'title': '空域抗干扰算法',
        'pdf': REPRO_DIR / '空域抗干扰算法.pdf',
        'theme': 'teal',
        'course': '结题 / repro / paper-reading-html',
        'hero_kicker': 'paper-reading-html · 精读模式',
        'hero_abstract': '这一篇真正要抓住的是结构：阵列模型、DOA、约束波束形成、结构化实现与等价关系。',
        'glossary': {
            '导向矢量': '阵列几何和来波方向之间的映射。',
            'DOA': 'Direction of Arrival，来波方向估计。',
            'MUSIC': '基于信号子空间与噪声子空间正交性的超分辨 DOA 方法。',
            'MVDR': 'Minimum Variance Distortionless Response。保目标、压其余方向功率。',
            'LCMV': 'Linearly Constrained Minimum Variance。把多个方向约束一起写进优化。',
            'GSC': 'Generalized Sidelobe Canceller。LCMV 的结构化实现。',
            'PI': 'Power Inversion。目标方向未知时的强干扰盲抑制路线。',
            '和差网络': '用和通道保目标，用差通道承载干扰和噪声，再做对消。',
        },
        'worksheet_cards': [],
        'chapters': [
            {'id': 'problem', 'index': '01', 'strap': '起点', 'title': '为什么空域处理能把同频同时间的信号分开', 'summary': '核心分离维度不是时间也不是频率，而是方向。', 'rows': []},
            {'id': 'array-model', 'index': '02', 'strap': '阵列模型', 'title': '阵列建模决定了后面所有算法的坐标系', 'summary': '只有先把阵列模型和 [[导向矢量]] 写清，后面估角和滤波才有共同语言。', 'rows': []},
            {'id': 'music', 'index': '03', 'strap': 'DOA', 'title': 'MUSIC 在这里先负责把方向找出来', 'summary': '先用 [[MUSIC]] 锁定角度，再让后续零陷和约束有准确落点。', 'rows': []},
            {'id': 'mvdr-lcmv-gsc', 'index': '04', 'strap': '主线方法', 'title': 'MVDR、LCMV、GSC 是同一条主线的连续展开', 'summary': '单约束最小方差起步，多约束推广，再变成更好实现的结构。', 'rows': []},
            {'id': 'pi-sd', 'index': '05', 'strap': '旁支与等价', 'title': 'PI 和和差网络讨论的是先验不足与结构实现', 'summary': '一条解决目标方向未知，一条把结构重新接回主线并证明等价。', 'rows': []},
        ],
    },
    {
        'slug': 'spatial-filter-simulation',
        'title': '空域滤波算法仿真',
        'pdf': REPRO_DIR / '空域滤波算法仿真.pdf',
        'theme': 'crimson',
        'course': '结题 / repro / paper-reading-html',
        'hero_kicker': 'paper-reading-html · 精读模式',
        'hero_abstract': '这篇仿真文档承担的是裁判工作：在统一场景下把算法排序和等价关系钉到图上。',
        'glossary': {
            'BER': 'Bit Error Rate，误码率。',
            'INR': 'Interference-to-Noise Ratio，干扰功率与噪声功率之比。',
            'MUSIC': '先估方向，再解释零陷和方向图。',
            'MVDR': '只对目标方向加无失真约束的最小方差路线。',
            'LCMV': '对多个方向同时施加约束的最小方差路线。',
            'GSC': 'LCMV 的结构化实现。',
            'PI': '目标方向未知时的直接抑制路线。',
            'SD': '文中基于和差网络的空域滤波实现。',
        },
        'worksheet_cards': [],
        'chapters': [
            {'id': 'setup', 'index': '01', 'strap': '仿真口径', 'title': '作者先把比较条件钉死', 'summary': '先统一场景，再比较算法，否则结果没有共同尺子。', 'rows': []},
            {'id': 'ber', 'index': '02', 'strap': 'BER', 'title': '误码率比较给出的不是绝对答案，而是相对排序', 'summary': '它真正回答的是在同一压力场景下谁更能保住 [[BER]]。', 'rows': []},
            {'id': 'pattern', 'index': '03', 'strap': '机理图', 'title': '方向图承担的是机理解释，而不是重复结论', 'summary': 'BER 告诉你谁赢了，方向图告诉你它为什么赢。', 'rows': []},
        ],
    },
]




OVERRIDE_FIRST_PAGE_LAYOUT = True

STYLE = r"""
:root {
  --bg: #f4efe4;
  --paper: #fffdf8;
  --ink: #1e1e1b;
  --muted: #635d52;
  --line: #d8cfbf;
  --accent: #8e5a2b;
  --accent-soft: #efe4d2;
  --note: #f8f1e6;
  --mark: #fff1a8;
  --shadow: 0 18px 40px rgba(57, 43, 23, 0.08);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--ink);
  background: linear-gradient(180deg, #efe6d5 0%, var(--bg) 28%, #f8f3eb 100%);
  font: 16px/1.8 "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
}
a { color: inherit; }
.top-nav {
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(12px);
  background: rgba(248, 243, 235, 0.9);
  border-bottom: 1px solid rgba(141, 114, 78, 0.18);
}
.top-nav-inner, .hero-panel, .content-shell, .home-shell {
  width: min(1480px, calc(100vw - 48px));
  margin: 0 auto;
}
.top-nav-inner {
  display: flex;
  gap: 18px;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
}
.nav-brand {
  text-decoration: none;
  font-size: 14px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 700;
}
.nav-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--muted);
  font-size: 14px;
}
.nav-link {
  text-decoration: none;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--paper);
  color: var(--accent);
}
.annot-shell, .home-shell { padding: 28px 0 44px; }
.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) 360px;
  gap: 24px;
  align-items: stretch;
  padding: 0 0 26px;
}
.hero-copy, .hero-preview, .toc-card, .summary-card, .map-card, .original-col, .translation-col, .note-col, .home-card, .board-intro {
  background: rgba(255,253,248,0.92);
  border: 1px solid rgba(142, 90, 43, 0.14);
  border-radius: 24px;
  box-shadow: var(--shadow);
}
.hero-copy { padding: 28px; }
.hero-kicker, .eyebrow, .section-kicker, .panel-kicker {
  margin: 0 0 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
  color: var(--accent);
  font-weight: 700;
}
.hero-copy h1, .home-card h2 {
  margin: 0 0 14px;
  line-height: 1.08;
}
.hero-copy h1 { font-size: clamp(30px, 5vw, 54px); }
.hero-abstract, .chapter-summary, .term-panel-body { color: var(--muted); }
.glossary-chip, .term-btn, .copy-btn {
  border: 1px solid #d5c0a5;
  background: white;
  border-radius: 999px;
  padding: 8px 12px;
  font: inherit;
  cursor: pointer;
}
.hero-preview {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.hero-preview img, .paper-figure img, .home-card img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 18px;
  border: 1px solid #eadfcd;
  object-fit: cover;
}
.hero-preview img {
  height: 100%;
  min-height: 220px;
  object-fit: cover;
  border-radius: 24px 24px 0 0;
  border: 0;
}
.hero-preview-copy { padding: 18px 20px 22px; }
.hero-preview-copy h2 { margin: 0 0 10px; font-size: 20px; }
.content-shell {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}
.toc-rail {
  position: sticky;
  top: 88px;
  display: grid;
  gap: 18px;
}
.toc-card { padding: 18px; }
.toc-links { display: grid; gap: 0; }
.toc-links a {
  display: block;
  text-decoration: none;
  color: var(--muted);
  padding: 8px 0;
  border-top: 1px solid rgba(216,207,191,0.7);
}
.toc-links a:first-child {
  border-top: 0;
  padding-top: 0;
}
.main-flow {
  display: grid;
  gap: 26px;
}
.board-intro {
  padding: 22px;
}
.board-intro h2 {
  margin: 0 0 10px;
  font-size: 26px;
}
.summary-grid, .map-grid, .home-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}
.summary-card, .map-card, .home-card {
  padding: 20px;
}
.summary-card h3, .map-card h3, .home-card h2 { margin: 0 0 10px; }
.summary-card p, .map-card p, .home-card p {
  margin: 0;
  color: var(--muted);
}
.section-stack {
  display: grid;
  gap: 26px;
}
.reading-row {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(300px, 0.85fr);
  gap: 22px;
  align-items: start;
}
.reading-row.has-translation {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(300px, 0.85fr);
}
.original-col, .translation-col, .note-col { padding: 24px; }
.note-col {
  position: sticky;
  top: 88px;
  padding: 20px;
}
.original-col h2, .translation-col h2 {
  margin: 0 0 16px;
  font-size: 28px;
  line-height: 1.2;
}
.chapter-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 14px;
  font-weight: 700;
}
.paper-flow p, .paper-flow li, .translation-flow p {
  margin: 0 0 12px;
  line-height: 1.9;
  color: #2d2a24;
}
.paper-flow p:last-child, .translation-flow p:last-child { margin-bottom: 0; }
.paper-flow ul { padding-left: 22px; margin: 10px 0 18px; }
.paper-flow a { color: var(--accent); }
.translation-flow p { color: var(--muted); }
.media-stack, .figure-gallery, .glossary-flow {
  display: grid;
  gap: 14px;
}
.media-stack { margin-top: 18px; }
.formula-block {
  padding: 16px 18px;
  border-radius: 18px;
  background: #fbf6ec;
  border: 1px solid #eadfcd;
}
.formula-head {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.formula-caption {
  margin: 0;
  font-weight: 700;
  color: var(--ink);
}
.formula-note { margin: 10px 0 0; color: var(--muted); }
.formula-display { overflow-x: auto; }
.paper-figure {
  margin: 0;
  padding: 16px;
  background: #fbf6ec;
  border: 1px solid #eadfcd;
  border-radius: 18px;
}
.paper-figure figcaption {
  margin-top: 10px;
  color: var(--muted);
  line-height: 1.75;
}
.note-card {
  padding: 16px 18px;
  border-radius: 18px;
  background: var(--note);
  border: 1px solid #eadfcd;
  margin-bottom: 14px;
}
.note-head {
  color: var(--accent);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 8px;
}
.note-card p {
  margin: 0 0 10px;
  line-height: 1.8;
  color: var(--muted);
}
.note-card p:last-child { margin-bottom: 0; }
mark {
  background: linear-gradient(180deg, transparent 35%, var(--mark) 35% 100%);
  padding: 0 2px;
}
.home-card {
  display: grid;
  gap: 14px;
}
.home-card a {
  display: inline-flex;
  width: fit-content;
  text-decoration: none;
  color: var(--accent);
  font-weight: 700;
}
.glossary-flow {
  display: flex;
  flex-wrap: wrap;
}
.term-panel {
  position: fixed;
  right: 16px;
  bottom: 16px;
  width: min(360px, calc(100vw - 32px));
  padding: 18px;
  border-radius: 22px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(34,31,26,0.96);
  box-shadow: 0 24px 48px rgba(0,0,0,0.24);
  color: white;
}
.term-panel-title { margin: 0 0 8px; }
.term-panel-body { color: rgba(255,255,255,0.84); }
.term-close {
  position: absolute;
  right: 12px;
  top: 12px;
  border: 0;
  background: transparent;
  color: white;
  font-size: 20px;
  cursor: pointer;
}
@media (max-width: 1180px) {
  .content-shell { grid-template-columns: 1fr; }
  .toc-rail { position: static; }
  .hero-panel, .reading-row, .reading-row.has-translation { grid-template-columns: 1fr; }
  .note-col { position: static; }
}
@media (max-width: 720px) {
  .top-nav-inner, .hero-panel, .content-shell, .home-shell { width: min(calc(100vw - 20px), 1480px); }
}
"""


def note_card(head: str, rows: list[tuple[str, str]], glossary: dict[str, str]) -> str:
    body = ''.join(f"<p><strong>{html.escape(label)}</strong> {rich(text, glossary)}</p>" for label, text in rows if text)
    return f"<div class='note-card'><div class='note-head'>{html.escape(head)}</div>{body}</div>"


def formula_html(item: dict[str, str], glossary: dict[str, str]) -> str:
    note = f"<p class='formula-note'>{rich(item.get('note', ''), glossary)}</p>" if item.get('note') else ''
    return (
        "<div class='formula-block'>"
        "<div class='formula-head'>"
        f"<div class='formula-caption'>{html.escape(item['caption'])}</div>"
        f"<button type='button' class='copy-btn' data-latex='{esc_attr(item['latex'])}'>复制 LaTeX</button>"
        "</div>"
        f"<div class='formula-display'>\\[{html.escape(item['latex'])}\\]</div>"
        f"{note}</div>"
    )


def figure_gallery(paper_slug: str, paper_pdf: Path, chapter_id: str, row_index: int, glossary: dict[str, str]) -> str:
    figures = FIGURE_MAP.get((paper_slug, chapter_id, row_index), [])
    if not figures:
        return ''
    blocks = []
    for item in figures:
        images = ensure_embedded_figures(paper_slug, paper_pdf, item['page'])
        for idx, rel in enumerate(images or [''], 1):
            if not rel:
                continue
            caption = item['caption'] if len(images) == 1 else f"{item['caption']} · 图块 {idx}"
            blocks.append(
                "<figure class='paper-figure'>"
                f"<img src='{rel}' alt='{esc_attr(caption)}'>"
                f"<figcaption>{rich(caption, glossary)}</figcaption>"
                "</figure>"
            )
    return f"<div class='figure-gallery'>{''.join(blocks)}</div>" if blocks else ''


def figure_note_cards(paper_slug: str, chapter_id: str, row_index: int, glossary: dict[str, str]) -> str:
    figures = FIGURE_MAP.get((paper_slug, chapter_id, row_index), [])
    if not figures:
        return ''
    cards = []
    for idx, item in enumerate(figures, 1):
        rows = [("对象", item['caption']), *list(item['analysis'].items())]
        cards.append(note_card(f"图解 {idx}", rows, glossary))
    return ''.join(cards)


def row_html(
    row: dict,
    glossary: dict[str, str],
    paper_slug: str,
    paper_pdf: Path,
    chapter: dict,
    row_index: int,
) -> str:
    has_translation = bool(row.get('translation'))
    row_id = chapter['id'] if row_index == 0 else f"{chapter['id']}-r{row_index + 1}"
    row_label = f"P{row_index + 1}"
    cols = [
        "<div class='original-col'>"
        f"<div class='section-kicker'>原文带读 · {row_label}</div>"
        + (
            f"<div class='chapter-chip'>{html.escape(chapter['index'])} · {html.escape(chapter['strap'])}</div>"
            f"<h2>{html.escape(chapter['title'])}</h2>"
            if row_index == 0 else ""
        )
        + f"<div class='paper-flow'>{paras(row['original'], glossary)}</div>"
        + f"<div class='media-stack'>{''.join(formula_html(item, glossary) for item in row.get('formulas', []))}{figure_gallery(paper_slug, paper_pdf, chapter['id'], row_index, glossary)}</div>"
        + "</div>"
    ]
    if has_translation:
        cols.append(
            "<div class='translation-col'>"
            f"<div class='section-kicker'>中文翻译 · {row_label}</div>"
            f"<div class='translation-flow'>{paras(row['translation'], glossary)}</div>"
            "</div>"
        )
    note_cards = []
    if row_index == 0:
        note_cards.append(
            note_card(
                "这一节",
                [
                    ("章节位置", f"{chapter['index']} · {chapter['strap']}"),
                    ("这一节在做什么", chapter['summary']),
                    ("读的时候盯住", "先看原文到底在建什么模型、证什么关系、落什么结论，再看右侧卡片里的逻辑层次和边界。"),
                ],
                glossary,
            )
        )
    note_cards.append(note_card(row_label, list(row['analysis'].items()), glossary))
    note_cards.append(figure_note_cards(paper_slug, chapter['id'], row_index, glossary))
    cols.append(
        "<aside class='note-col'>"
        f"<div class='section-kicker'>带读 · {row_label}</div>"
        f"{''.join(note_cards)}"
        "</aside>"
    )
    cls = "reading-row has-translation" if has_translation else "reading-row"
    return f"<section id='{row_id}' class='{cls}'>{''.join(cols)}</section>"


def toc(chapters: list[dict]) -> str:
    items = [
        "<a href='#document-reading'>文档解读</a>",
        "<a href='#guided-reading'>原文带读</a>",
    ]
    for chapter in chapters:
        items.append(f"<a href='#{chapter['id']}'><strong>{html.escape(chapter['index'])}</strong> {html.escape(chapter['title'])}</a>")
    return ''.join(items)


def chapter_map(chapters: list[dict], glossary: dict[str, str]) -> str:
    return ''.join(
        "<article class='map-card'>"
        f"<p class='eyebrow'>{html.escape(chapter['index'])} · {html.escape(chapter['strap'])}</p>"
        f"<h3>{html.escape(chapter['title'])}</h3>"
        f"<p>{rich(chapter['summary'], glossary)}</p>"
        "</article>"
        for chapter in chapters
    )


def overview_cards(cards: list[dict], glossary: dict[str, str]) -> str:
    return ''.join(
        "<article class='summary-card'>"
        f"<h3>{html.escape(card['label'])}</h3>"
        f"<p>{rich(card['body'], glossary)}</p>"
        "</article>"
        for card in cards
    )


def page(paper: dict, preview_name: str | None) -> str:
    glossary = paper['glossary']
    preview = (
        "<div class='hero-preview'>"
        f"<img src='{preview_name}' alt='{esc_attr(paper['title'])} 首页预览'>"
        "<div class='hero-preview-copy'><h2>网页结构</h2><p class='chapter-summary'>这一页沿用第一页的精读骨架：前面先看整篇解读，后面逐段对照原文和带读。</p></div>"
        "</div>"
        if preview_name else
        "<div class='hero-preview'><div class='hero-preview-copy'><h2>网页结构</h2><p class='chapter-summary'>这一页沿用第一页的精读骨架：前面先看整篇解读，后面逐段对照原文和带读。</p></div></div>"
    )
    sections = ''.join(
        row_html(row, glossary, paper['slug'], paper['pdf'], chapter, idx)
        for chapter in paper['chapters']
        for idx, row in enumerate(chapter['rows'])
    )
    body = (
        "<header class='top-nav'><div class='top-nav-inner'>"
        "<a href='../index.html' class='nav-brand'>Paper Reading HTML</a>"
        f"<div class='nav-meta'><span>{html.escape(paper['title'])}</span><span>{html.escape(paper.get('course', ''))}</span><a class='nav-link' href='../../{html.escape(paper['pdf'].name)}'>原 PDF</a></div>"
        "</div></header>"
        "<main class='annot-shell'>"
        f"<section class='hero-panel'><div class='hero-copy'><p class='hero-kicker'>{html.escape(paper.get('hero_kicker', 'paper-reading-html · 精读模式'))}</p><h1>{html.escape(paper['title'])}</h1><p class='hero-abstract'>{rich(paper.get('hero_abstract', ''), glossary)}</p></div>{preview}</section>"
        "<div class='content-shell'><aside class='toc-rail'><div class='toc-card'><p class='eyebrow'>章节导航</p><nav class='toc-links'>"
        f"{toc(paper['chapters'])}</nav></div><div class='toc-card'><p class='eyebrow'>术语点击解释</p><div class='glossary-flow'>"
        f"{''.join(f'<button type=\'button\' class=\'glossary-chip term-btn\' data-term=\'{esc_attr(term)}\' data-definition=\'{esc_attr(defn)}\'>{html.escape(term)}</button>' for term, defn in paper['glossary'].items())}</div></div></aside>"
        "<section class='main-flow'>"
        "<section id='document-reading' class='summary-board'>"
        "<div class='board-intro'><p class='eyebrow'>Board 2</p><h2>文档解读</h2><p class='chapter-summary'>先把全文压成 thesis、方法链、证据链和边界，再回到原文逐段带读。这样读起来不会只见公式，不见主线。</p></div>"
        f"<div class='summary-grid'>{overview_cards(paper.get('overview_cards', paper.get('worksheet_cards', [])), glossary)}</div>"
        "<div class='board-intro'><p class='eyebrow'>章节逻辑地图</p><h2>这一篇是怎么往下推进的</h2><p class='chapter-summary'>这里不重复标题，而是说明每一节在整篇论证里承担什么角色。</p></div>"
        f"<div class='map-grid'>{chapter_map(paper['chapters'], glossary)}</div>"
        "</section>"
        f"<section id='guided-reading' class='section-stack'>{sections}</section></section></div></main>"
    )
    return shell(f"{paper['title']} | Paper Reading HTML", body)


def home(cards: str) -> str:
    body = (
        "<main class='home-shell'><section class='hero-copy'><p class='hero-kicker'>paper-reading-html · 精读模式</p><h1>论文网页化入口</h1><p class='hero-abstract'>这里收的是精读型网页，不是展示型主页。每篇页面都保留整篇解读和逐段带读两块。</p></section><section class='home-grid'>"
        f"{cards}</section></main>"
    )
    return shell('Paper Reading HTML', body)


def main() -> None:
    ensure_dir(OUTPUT_DIR)
    cards = []
    for paper in PAPERS:
        out_dir = ensure_dir(OUTPUT_DIR / paper['slug'])
        preview = ensure_preview(paper['slug'], paper['pdf'])
        html_text = page(paper, preview)
        (out_dir / 'index.html').write_text(html_text, encoding='utf-8')
        cards.append(
            "<article class='home-card'>"
            + (f"<figure><img src='{preview}' alt='{esc_attr(paper['title'])} 预览'></figure>" if preview else '')
            + f"<p class='eyebrow'>{html.escape(paper.get('course', ''))}</p><h2>{html.escape(paper['title'])}</h2><p>{html.escape(paper.get('hero_abstract', ''))}</p><a href='./{paper['slug']}/index.html'>打开网页</a></article>"
        )
    (OUTPUT_DIR / 'index.html').write_text(home(''.join(cards)), encoding='utf-8')


if __name__ == '__main__':
    main()

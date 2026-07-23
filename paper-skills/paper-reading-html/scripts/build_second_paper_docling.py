
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

ROOT = Path(r"D:\study\A_finalyear_prj")
EXTRACT_DIR = ROOT / "结题" / "document" / "repro" / "paper2web" / "extracted" / "spatial-anti-jamming"
DOC_MD = EXTRACT_DIR / "docling" / "paper-cabb7cdd.md"
IMG_SRC_DIR = ROOT / "tmp" / "spatial_anti_jamming_images"
PAGE_SRC_DIR = ROOT / "tmp" / "spatial_anti_jamming_pdfimages"
OUT_DIR = ROOT / "结题" / "document" / "repro" / "paper2web" / "spatial-anti-jamming"
ASSET_DIR = OUT_DIR / "docling-assets"
PREVIEW_DIR = ASSET_DIR / "pages"
FIG_DIR = ASSET_DIR / "figures"
OUT_HTML = OUT_DIR / "index.html"
PDF_REL = "../../空域抗干扰算法.pdf"

SECTION_NOTES = {
    "空域抗干扰的目的：": [
        ("这一节在做什么", "先把全文的任务定下来：为什么要用空域、空域到底解决什么、最后要保住什么。"),
        ("逻辑主线", "作者不是先上算法，而是先说明只有在干扰和目标方向可分时，空域处理才成立。"),
        ("读完要记住", "后面的所有方法都围着三件事转：建模、估角、保目标同时压干扰。"),
    ],
    "算法目标需要完成：": [
        ("这一节在做什么", "把全文目标压成三条工程要求，不让后面的方法讨论失焦。"),
        ("逻辑主线", "先建对阵列模型，再找对方向，最后设计出不伤目标的滤波器。"),
        ("读完要记住", "这不是单个算法问题，而是一整条处理链。"),
    ],
    "一、阵列接收机模型": [
        ("这一节在做什么", "进入空域链路的前提层，先把阵列接收模型和导向矢量语言建起来。"),
        ("逻辑主线", "后面的 MUSIC、MVDR、LCMV、GSC 都默认这里的几何模型是对的。"),
        ("读完要记住", "模型错了，后面角度估计和零陷位置都会跟着错。"),
    ],
    "1.1 阵列接收机的数学模型": [
        ("这一节在做什么", "把阵元位置、传播方向、时延、相位差和导向矢量一项项写出来。"),
        ("逻辑主线", "先从几何关系得到相位差，再把它收成阵列的导向矢量。"),
        ("读完要记住", "导向矢量不是装饰，它是后面所有空域算法共同使用的方向描述。"),
    ],
    "1.2 各种阵列天线对应的导向矢量": [
        ("这一节在做什么", "把导向矢量从抽象符号落到线阵、圆阵、面阵三种常见几何上。"),
        ("逻辑主线", "阵列几何一变，导向矢量就变，算法理解方向的语言也跟着变。"),
        ("读完要记住", "这一步是在提醒你：不同阵列不是同一公式换个名字。"),
    ],
    "二、空间谱与 DOA 估计": [
        ("这一节在做什么", "把问题从几何建模推进到方向估计。"),
        ("逻辑主线", "只有先估对 DOA，后面的波束和零陷才能落到正确角度。"),
        ("读完要记住", "空域滤波不是盲打，它依赖前面的方向信息。"),
    ],
    "2.1 空间谱": [
        ("这一节在做什么", "解释空间谱是什么，以及为什么阵列信号也能像时域信号那样做一种“频谱式”分析。"),
        ("逻辑主线", "把阵列输出理解成不同导向向量的叠加，再通过搜索谱峰拿到角度。"),
        ("读完要记住", "空间谱的峰对应可能来波方向，但主瓣宽度会限制分辨能力。"),
    ],
    "2.2.1 MUSIC 算法": [
        ("这一节在做什么", "用子空间分解把 DOA 估计写成谱峰搜索问题。"),
        ("逻辑主线", "先分出信号子空间和噪声子空间，再用正交性构造 MUSIC 谱。"),
        ("读完要记住", "MUSIC 的强处来自子空间结构，不是普通扫描。"),
    ],
    "三、空域滤波算法": [
        ("这一节在做什么", "从 DOA 估计转到真正执行抑制的滤波器设计。"),
        ("逻辑主线", "先给出统一滤波模型，再依次展开 MVDR、LCMV、GSC、PI 和和差网络。"),
        ("读完要记住", "这一章真正讨论的是怎样在保目标的前提下压干扰。"),
    ],
    "3.1 空域滤波数学模型": [
        ("这一节在做什么", "把空域滤波器抽象成输入向量、权向量和输出功率之间的关系。"),
        ("逻辑主线", "后面各种算法只是对同一个输出功率最小化问题加不同约束。"),
        ("读完要记住", "先有这个统一模型，后面的算法比较才有共同坐标。"),
    ],
    "3.2.1 MVDR 空域滤波算法": [
        ("这一节在做什么", "给出单约束最小方差的基本形式。"),
        ("逻辑主线", "保证目标方向无失真通过，同时让输出总功率尽量小。"),
        ("读完要记住", "MVDR 是主线起点，它统一了“保目标”和“压其余方向”。"),
    ],
    "3.2.2 LCMV 空域滤波算法": [
        ("这一节在做什么", "把 MVDR 的单约束扩展成多约束。"),
        ("逻辑主线", "不仅保目标，还能把已知干扰方向直接压零。"),
        ("读完要记住", "LCMV 更强，但自由度会被约束吃掉。"),
    ],
    "3.2.3 GSC 算法": [
        ("这一节在做什么", "把 LCMV 重写成更适合实现的结构。"),
        ("逻辑主线", "固定主支路负责满足约束，阻塞矩阵和自适应支路负责消干扰。"),
        ("读完要记住", "GSC 不是换目标函数，而是换实现结构。"),
    ],
    "3.2.4 PI 空域滤波算法": [
        ("这一节在做什么", "讨论目标方向未知时怎么办。"),
        ("逻辑主线", "不再显式保护目标，只求总输出功率最小，从而盲抑制强干扰。"),
        ("读完要记住", "PI 的代价也很直接：压干扰时容易顺手压伤目标。"),
    ],
    "3.2.5 基于和差网络的空域滤波算法": [
        ("这一节在做什么", "把 PI 重新接回目标方向先验，用和通道保目标、差通道承载干扰。"),
        ("逻辑主线", "先主瓣对准目标，再在差通道做对消。"),
        ("读完要记住", "这里真正重要的是结构分工，不是名字本身。"),
    ],
    "3.3 MVDR 算法与基于和差网络的空域滤波算法等价的证明": [
        ("这一节在做什么", "把前面的工程结构重新接回主线理论。"),
        ("逻辑主线", "证明和差网络的等效权向量与 MVDR 的权向量一致。"),
        ("读完要记住", "这篇文档最有价值的地方之一，就是把结构实现和主线理论连成同一个问题。"),
    ],
}

SUMMARY_CARDS = [
    ("一句话 thesis", "这篇文档真正做的，不是把一串空域算法排队报名字，而是把 **阵列建模 → DOA → 约束波束形成 → 结构化实现与等价性** 串成一条完整链。"),
    ("问题起点", "当目标信号和干扰信号在时间、频率上都难分时，只要它们的 **到达方向不同**，就还能在空域上分开。"),
    ("主线方法", "主线是 **MVDR → LCMV → GSC**：先单约束最小方差，再扩成多约束，最后变成更适合实现的结构。"),
    ("旁支方法", "**PI** 解决的是目标方向未知时的强干扰盲抑制；**和差网络** 则把目标方向先验重新接回系统。"),
    ("最值得记住的结论", "这篇材料最难得的不是罗列方法，而是把 **和差网络与 MVDR 的等价性** 说清了。"),
]

FIG_NOTES = {
    0: [("图里是什么", "阵列接收机的几何模型图。"), ("看图重点", "坐标原点、阵元位置、入射方向以及由此引出的时延和相位差。"), ("这图说明什么", "作者先从几何关系建模，而不是直接空谈滤波器。")],
    1: [("图里是什么", "不同阵列几何示意图。"), ("看图重点", "线阵、圆阵、面阵的阵元排布不同，因此导向矢量形式不同。"), ("这图说明什么", "不同阵列不是同一公式换壳，而是不同几何约束。")],
    2: [("图里是什么", "空域滤波统一结构示意。"), ("看图重点", "输入阵列信号、权向量调节以及最终输出。"), ("这图说明什么", "后面的 MVDR、LCMV、GSC 都是在这套统一结构上改约束。")],
    3: [("图里是什么", "GSC 结构图。"), ("看图重点", "主支路、阻塞矩阵、自适应支路之间的分工。"), ("这图说明什么", "GSC 的优势来自结构分解，不是另一套完全不同的目标函数。")],
    4: [("图里是什么", "PI 波束形成结构图。"), ("看图重点", "第一通道保留原始合成信号，其余通道通过调权压低总输出功率。"), ("这图说明什么", "PI 在目标方向未知时也能工作，但代价是容易连目标一起压。")],
    5: [("图里是什么", "和差网络空域滤波结构图。"), ("看图重点", "和通道保目标，差通道承载干扰和噪声，再做对消。"), ("这图说明什么", "它把盲抑制结构重新接回目标方向先验，并最终与 MVDR 对上。")],
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def rich(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def slug(text: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", text).strip("-")
    return cleaned or "section"


def clean_title(line: str) -> str:
    return re.sub(r"^#+\s*", "", line).strip()


def paragraph_rows(paragraph: str) -> list[tuple[str, str]]:
    text = paragraph.strip()
    rows = [("这段在说什么", text)]
    if any(key in text for key in ["相位", "时延", "导向矢量", "阵元"]):
        rows.append(("读法", "这里先不要急着记公式，先看作者是在从几何关系推到阵列的方向描述语言。"))
    elif any(key in text for key in ["空间谱", "谱峰", "DOA", "角度"]):
        rows.append(("读法", "这一段真正关心的是怎样从阵列输出反推出方向，而不是把空间谱只当作名词。"))
    elif any(key in text for key in ["MVDR", "LCMV", "GSC", "PI"]):
        rows.append(("读法", "这里要盯住约束条件、优化目标和工程代价三件事。"))
    elif any(key in text for key in ["等价", "证明"]):
        rows.append(("读法", "作者在做的不是新增算法，而是把不同结构收回同一个理论框架。"))
    else:
        rows.append(("读法", "这一段先看它承接前文哪一步，再看它把问题推进到了哪里。"))
    return rows


def parse_sections(text: str) -> list[dict]:
    lines = text.splitlines()
    sections: list[dict] = []
    current: dict | None = None
    image_idx = 0

    def ensure_section(title: str) -> dict:
        nonlocal current
        current = {"title": title, "id": slug(title), "blocks": []}
        sections.append(current)
        return current

    def add_paragraph(buf: list[str]) -> None:
        if not buf or current is None:
            return
        paragraph = " ".join(part.strip() for part in buf if part.strip())
        if paragraph:
            current["blocks"].append({"type": "paragraph", "text": paragraph})

    buf: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            add_paragraph(buf)
            buf = []
            ensure_section(clean_title(stripped))
            continue
        if current is None:
            ensure_section("导言")
        if stripped == "<!-- image -->":
            add_paragraph(buf)
            buf = []
            current["blocks"].append({"type": "image", "index": image_idx})
            image_idx += 1
            continue
        if stripped == "<!-- formula-not-decoded -->":
            add_paragraph(buf)
            buf = []
            current["blocks"].append({"type": "formula-missing"})
            continue
        if not stripped:
            add_paragraph(buf)
            buf = []
            continue
        buf.append(stripped)
    add_paragraph(buf)
    return sections


def section_notes(title: str) -> list[tuple[str, str]]:
    return SECTION_NOTES.get(title, [("这一节在做什么", "这一节按抽取结果保留原文顺序，并在右侧按段落解释逻辑。")])


def render_original_block(block: dict) -> str:
    if block["type"] == "paragraph":
        return f"<p>{rich(block['text'])}</p>"
    if block["type"] == "image":
        src = f"docling-assets/figures/img-{block['index']:03d}.png"
        return f"<figure class='paper-figure'><img src='{src}' alt='原文插图 {block['index'] + 1}'><figcaption>原文插图 {block['index'] + 1}</figcaption></figure>"
    if block["type"] == "formula-missing":
        return "<div class='formula-missing'>原 PDF 此处为公式推导，当前抽取未完整还原，保留这一占位提醒你回看原 PDF 或页图。</div>"
    return ""


def render_note_cards(section: dict) -> str:
    cards = []
    cards.append("<div class='note-card'><div class='note-head'>这一节</div>" + ''.join(f"<p><strong>{esc(k)}</strong> {rich(v)}</p>" for k, v in section_notes(section['title'])) + "</div>")
    para_no = 1
    fig_no = 0
    for block in section['blocks']:
        if block['type'] == 'paragraph':
            rows = paragraph_rows(block['text'])
            cards.append("<div class='note-card'><div class='note-head'>P%d</div>%s</div>" % (para_no, ''.join(f"<p><strong>{esc(k)}</strong> {rich(v)}</p>" for k, v in rows)))
            para_no += 1
        elif block['type'] == 'image':
            rows = FIG_NOTES.get(fig_no, [("图里是什么", "这是这一节对应的原文插图。"), ("看图重点", "先看它和前后段落在哪一步对应。"), ("这图说明什么", "它通常承担结构说明或算法机理说明。")])
            cards.append("<div class='note-card'><div class='note-head'>图解 %d</div>%s</div>" % (fig_no + 1, ''.join(f"<p><strong>{esc(k)}</strong> {rich(v)}</p>" for k, v in rows)))
            fig_no += 1
        elif block['type'] == 'formula-missing':
            cards.append("<div class='note-card'><div class='note-head'>公式提醒</div><p><strong>当前状态</strong> 这一处原 PDF 里的公式链较密，Docling 没有把它完整转成可读公式。</p><p><strong>怎么读</strong> 先抓住这段想证明的对象和结论，再配合原 PDF 看公式细节。</p></div>")
    return ''.join(cards)


def render_section(section: dict, idx: int) -> str:
    original = ''.join(render_original_block(block) for block in section['blocks'])
    return (
        f"<section id='{section['id']}' class='reading-row'>"
        "<div class='original-col'>"
        f"<div class='section-kicker'>原文带读 · S{idx}</div>"
        f"<h2>{rich(section['title'])}</h2>"
        f"<div class='paper-flow'>{original}</div>"
        "</div>"
        "<aside class='note-col'>"
        f"<div class='section-kicker'>带读 · S{idx}</div>{render_note_cards(section)}"
        "</aside>"
        "</section>"
    )


def build_html(sections: list[dict]) -> str:
    toc = ''.join(f"<a href='#{section['id']}'>{rich(section['title'])}</a>" for section in sections)
    cards = ''.join(f"<article class='summary-card'><h3>{esc(title)}</h3><p>{rich(body)}</p></article>" for title, body in SUMMARY_CARDS)
    sections_html = ''.join(render_section(section, i + 1) for i, section in enumerate(sections))
    return f"""<!DOCTYPE html>
<html lang='zh-CN'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>空域抗干扰算法 | Paper Reading HTML</title>
<style>
:root {{ --bg:#f4efe4; --paper:#fffdf8; --ink:#1e1e1b; --muted:#635d52; --line:#d8cfbf; --accent:#8e5a2b; --accent-soft:#efe4d2; --note:#f8f1e6; --shadow:0 18px 40px rgba(57,43,23,.08); }}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:linear-gradient(180deg,#efe6d5 0%, var(--bg) 28%, #f8f3eb 100%); font:16px/1.8 "PingFang SC","Microsoft YaHei",sans-serif; }}
a {{ color:inherit; }}
.topbar {{ position:sticky; top:0; z-index:10; backdrop-filter:blur(12px); background:rgba(248,243,235,.9); border-bottom:1px solid rgba(141,114,78,.18); }}
.topbar-inner,.hero,.layout {{ width:min(1480px, calc(100vw - 48px)); margin:0 auto; }}
.topbar-inner {{ display:flex; justify-content:space-between; gap:16px; padding:14px 0; align-items:center; }}
.brand {{ font-size:14px; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); font-weight:700; }}
.meta {{ display:flex; gap:12px; flex-wrap:wrap; color:var(--muted); font-size:14px; }}
.meta a {{ text-decoration:none; padding:8px 12px; border:1px solid var(--line); border-radius:999px; background:var(--paper); color:var(--accent); }}
.shell {{ padding:28px 0 44px; }}
.hero {{ display:grid; grid-template-columns:minmax(0,1.4fr) 360px; gap:24px; margin-bottom:24px; }}
.hero-copy,.hero-side,.toc-card,.summary-card,.original-col,.note-col {{ background:rgba(255,253,248,.92); border:1px solid rgba(142,90,43,.14); border-radius:24px; box-shadow:var(--shadow); }}
.hero-copy {{ padding:28px; }}
.hero-kicker,.eyebrow,.section-kicker {{ margin:0 0 10px; letter-spacing:.08em; text-transform:uppercase; font-size:12px; color:var(--accent); font-weight:700; }}
.hero-copy h1 {{ margin:0 0 14px; font-size:clamp(30px,5vw,54px); line-height:1.08; }}
.hero-copy p,.summary-card p,.note-card p,.toc-card p {{ color:var(--muted); }}
.hero-side img {{ width:100%; display:block; border-radius:24px 24px 0 0; }}
.hero-side-copy {{ padding:18px 20px 22px; }}
.layout {{ display:grid; grid-template-columns:260px minmax(0,1fr); gap:24px; align-items:start; }}
.rail {{ position:sticky; top:88px; display:grid; gap:18px; }}
.toc-card {{ padding:18px; }}
.toc-links a {{ display:block; text-decoration:none; color:var(--muted); padding:8px 0; border-top:1px solid rgba(216,207,191,.7); }}
.toc-links a:first-child {{ border-top:0; padding-top:0; }}
.main {{ display:grid; gap:24px; }}
.summary-grid {{ display:grid; gap:18px; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); }}
.summary-card {{ padding:20px; }}
.summary-card h3 {{ margin:0 0 10px; }}
.reading-row {{ display:grid; grid-template-columns:minmax(0,1.55fr) minmax(300px,.85fr); gap:22px; align-items:start; }}
.original-col {{ padding:24px; }}
.note-col {{ padding:20px; position:sticky; top:88px; }}
.original-col h2 {{ margin:0 0 16px; font-size:28px; line-height:1.2; }}
.paper-flow p {{ margin:0 0 12px; line-height:1.9; color:#2d2a24; }}
.paper-figure {{ margin:18px 0 12px; padding:16px; background:#fbf6ec; border:1px solid #eadfcd; border-radius:18px; }}
.paper-figure img {{ width:100%; border-radius:12px; display:block; background:white; }}
.paper-figure figcaption {{ margin-top:10px; color:var(--muted); }}
.note-card {{ padding:16px 18px; border-radius:18px; background:var(--note); border:1px solid #eadfcd; margin-bottom:14px; }}
.note-head {{ color:var(--accent); font-size:13px; font-weight:700; margin-bottom:8px; }}
.note-card p {{ margin:0 0 10px; line-height:1.8; }}
.note-card p:last-child {{ margin-bottom:0; }}
.formula-missing {{ margin:18px 0; padding:14px 16px; border-radius:16px; border:1px dashed #d1b48f; background:#fff6ea; color:var(--muted); }}
@media (max-width:1180px) {{ .layout,.hero,.reading-row {{ grid-template-columns:1fr; }} .rail,.note-col {{ position:static; }} }}
</style>
</head>
<body>
<header class='topbar'><div class='topbar-inner'><div class='brand'>Paper Reading HTML</div><div class='meta'><span>空域抗干扰算法</span><span>第二篇重跑 · Docling 原文抽取</span><a href='{PDF_REL}'>原 PDF</a></div></div></header>
<main class='shell'>
<section class='hero'>
<div class='hero-copy'><p class='hero-kicker'>paper-reading-html · 第二篇重跑</p><h1>空域抗干扰算法</h1><p>这次不再沿用之前的手工结构数据，而是直接以 <strong>Docling 抽取出的原文顺序</strong> 重建第二篇。原文列保留抽取出的段落和插图，右侧再按节和段落解释它到底在说什么。</p></div>
<div class='hero-side'><img src='docling-assets/pages/page-01.png' alt='空域抗干扰算法首页预览'><div class='hero-side-copy'><h2>这一版的重点</h2><p>先把第二篇的原文层立起来，再让带读和整篇解读跟着原文走，而不是反过来拿摘要去拼网页。</p></div></div>
</section>
<div class='layout'>
<aside class='rail'>
<div class='toc-card'><p class='eyebrow'>章节导航</p><nav class='toc-links'><a href='#document-reading'>文档解读</a><a href='#guided-reading'>原文带读</a>{toc}</nav></div>
</aside>
<section class='main'>
<section id='document-reading'><div class='summary-grid'>{cards}</div></section>
<section id='guided-reading'>{sections_html}</section>
</section>
</div>
</main>
</body>
</html>"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for src in sorted(IMG_SRC_DIR.glob('img-*.png')):
        shutil.copy2(src, FIG_DIR / src.name)
    for src in sorted(PAGE_SRC_DIR.glob('page-*.png')):
        shutil.copy2(src, PREVIEW_DIR / src.name)
    sections = parse_sections(DOC_MD.read_text(encoding='utf-8'))
    OUT_HTML.write_text(build_html(sections), encoding='utf-8')


if __name__ == '__main__':
    main()

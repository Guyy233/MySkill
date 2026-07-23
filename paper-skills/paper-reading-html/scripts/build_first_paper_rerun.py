from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

ROOT = Path(r"D:\study\A_finalyear_prj")
MARKER_DIR = ROOT / "tmp" / "marker_test_tf" / "时频域干扰抑制算法"
MARKDOWN_PATH = MARKER_DIR / "时频域干扰抑制算法.md"
OUTPUT_DIR = ROOT / "结题" / "document" / "repro" / "paper2web" / "time-frequency-interference"
OUTPUT_HTML = OUTPUT_DIR / "index.html"
LEGACY_HTML = OUTPUT_DIR / "index-legacy.html"
ASSET_DIR = OUTPUT_DIR / "marker-assets"
PREVIEW_REL = "../assets/previews/time-frequency-interference-01.png"
PDF_REL = "../../时频域干扰抑制算法.pdf"

SECTION_NOTES = {
    "1": {
        "这部分在做什么": "先把全文拆成频域和时域两条链。真正的主线不是某一个公式，而是检测、抑制、性能评估这一整条工程闭环。",
        "最该抓住的点": "频域负责单音和窄带干扰，时域负责高斯脉冲干扰。不同干扰要在最显眼的域里处理。",
        "工程判断": "作者从一开始就没有追求复杂重建，而是优先追求能检测、能切除、能仿真的稳妥路线。",
    },
    "1.1": {
        "这部分在做什么": "频域部分先处理怎么把干扰看清，再处理怎么把干扰切掉，最后用 BER 曲线量化代价。",
        "最该抓住的点": "窗口、门限、平滑和置零是频域链路的四个关键控制点。",
        "工程判断": "如果干扰在频谱上足够尖锐，能量检测和置零会非常有效；如果干扰变宽，副作用会同步上升。",
    },
    "1.1.1": {
        "这部分在做什么": "这一节解释 CME 和 FCME 为什么能工作。核心不是名字，而是先估背景、再剔离群点。",
        "最该抓住的点": "门限因子和虚警概率直接绑定。门限设太低会误杀有用频点，设太高会漏检干扰。",
        "工程判断": "文中最后选 CME，不是因为它绝对最强，而是因为它和 FCME 性能接近，但更省复杂度。",
    },
    "1.1.2": {
        "这部分在做什么": "这一节把检测结果真正变成抑制动作。作者选择最直接的置零，而不是估计后补偿。",
        "最该抓住的点": "频域置零的收益很大，但代价是有效频点也会被一起切掉。",
        "工程判断": "对单音和较窄带干扰，这种代价可接受；带宽一旦变大，损伤会快速放大。",
    },
    "1.1.3": {
        "这部分在做什么": "这里不是展示图多，而是在回答一个工程问题：干扰压下去以后，链路 BER 值不值得。",
        "最该抓住的点": "1%、5%、10% 一类局部窄带干扰下，BER 回退仍然控制在较小范围。",
        "工程判断": "这说明频域链路的有效范围是局部集中干扰，而不是任意宽带干扰。",
    },
    "1.2": {
        "这部分在做什么": "时域部分把问题换成脉冲干扰，重点从带宽转成周期、持续时间和占空比。",
        "最该抓住的点": "时域仍然沿用 CME 加置零，但统计对象从频点变成时域样点。",
        "工程判断": "同样叫置零，频域损失的是子载波，时域损失的是时间连续性。",
    },
    "1.2.1": {
        "这部分在做什么": "这一节讨论如何检测脉冲干扰，以及为什么还要比较整段检测和分段检测。",
        "最该抓住的点": "占空比越大，脉冲样点越不尖锐，检测难度越高。分段长度如果贴近周期，性能会更好。",
        "工程判断": "分段不只是为了省算力，它会改变统计集合本身，所以会直接改变检测效果。",
    },
    "1.2.2": {
        "这部分在做什么": "这一节说明时域抑制的最终准则不是波形好不好看，而是 BER 是否真的回收。",
        "最该抓住的点": "低占空比下，置零能显著减轻脉冲干扰；高占空比下，自身损伤会很快抬头。",
        "工程判断": "文中最后给出的不是万能算法，而是一组可工作参数区间。",
    },
}

FIGURE_NOTES = {
    19: "这是频域总流程图。你要从左到右看成一条工程流水线：接收数据先进入检测，再把检测结果交给抑制模块，最后回到后续接收链路。",
    20: "这张图强调的是 1/2 重叠加窗。作者不是把加窗当小修小补，而是把它当成减少频谱泄漏、稳住检测门限的前置条件。",
    21: "这张图最核心的差别在初始背景集合。CME 默认全体样点先都干净，FCME 先排序后只信低能量样点，所以 FCME 更保守。",
    22: "这里看的是漏检概率。图的意义不是谁绝对压倒谁，而是说明在本文的仿真口径下，CME 和 FCME 的检测能力非常接近。",
    23: "这里看的是虚警概率。和上一图合在一起读，作者才有理由说 FCME 的额外复杂度并没有换来足够大的收益。",
    24: "这张图解释为什么要平滑。平滑前频谱起伏剧烈，平滑后干扰带更连贯，但滑动因子过大又会把干扰能量抹到邻近有效频点。",
    25: "这张图是平滑因子的工作区间图。太小不够稳，太大伤邻频，中间一段才是较稳的参数区间。",
    26: "这张图说明带宽越宽，漏检越难压低。因为总干扰功率被摊到更多频点后，每个频点就不再足够突出。",
    27: "单音抑制图要看那个被切掉的尖峰。置零之后，目标频点附近出现明显凹陷，说明检测点和抑制点对上了。",
    28: "5% 窄带干扰抑制图主要看一段连续频带被准确切除，而不是只切掉最高尖峰。",
    29: "10% 窄带时，凹陷更宽，说明置零代价开始变大。这正是后面 BER 回退会增加的原因。",
    30: "这是频域整链路性能仿真的总流程。它告诉你后面的 BER 曲线不是孤立结果，而是建立在完整检测加抑制链条上的。",
    31: "这张 BER 图是频域部分最重要的收口。关键不是某个绝对值，而是随着干扰带宽变宽，曲线整体上移。",
    32: "这是时域总流程图。和频域不同，这里不再靠频点定位，而是直接在样点层面发现并切除脉冲。",
    33: "这张图解释了时域平滑的必要性。脉冲样点经过平滑后和噪声底分离更清楚，门限才更稳定。",
    34: "这张图的核心变量是占空比。占空比越高，漏检概率越难压低，因为脉冲在时域里不再足够稀疏。",
    35: "这张图解释为什么要比较不同分段长度。分段太短或太长都不好，贴近脉冲周期时检测最稳。",
}

SUMMARY_CARDS = [
    ("一句话 thesis", "这篇材料真正建立起来的，不是一个神奇新算法，而是一条 **检测 -> 抑制 -> BER 验证** 的可落地抗干扰链路。"),
    ("频域主线", "先加窗和 FFT，把窄带干扰变成频域尖峰，再用 **CME / FCME** 做能量检测，最后对被污染频点 **置零**。"),
    ("时域主线", "把高斯脉冲干扰写成带 **周期 / 持续时间 / 占空比** 的模型，再比较整段检测和分段检测。"),
    ("最重要的工程结论", "对局部集中干扰，这套方法有效；对带宽过宽或占空比过大的干扰，损伤和误差都会快速上升。"),
    ("这次重跑的含义", "这一版页面直接吃 **Marker 原文抽取**，把图片和可读公式重新接回网页，先恢复第一篇的可读性和可检查性。"),
]

GLOSSARY = {
    "CME": "Consecutive Mean Excision。先把样点看作背景，再迭代剔除高能异常点。",
    "FCME": "Forward CME。先排序，先相信低能量样点，再逐步扩展背景集合。",
    "FFT": "快速傅里叶变换。把时域数据转到频域，便于观察窄带干扰。",
    "BER": "Bit Error Rate，误码率。最后衡量算法是否真的保住链路。",
    "JNR": "Jamming-to-Noise Ratio，干扰功率与噪声功率之比。",
    "OFDM": "正交频分复用。本文实验链路使用的基带体制。",
    "Hanning窗": "常用加窗方法，用来减轻频谱泄漏。",
    "置零": "把已判定为受干扰的频点或样点直接设为 0。",
    "虚警概率": "本来不是干扰却被判成干扰的概率。",
    "漏检概率": "本来是干扰却没有被检出来的概率。",
    "占空比": "一个干扰周期内，干扰持续时间占整个周期的比例。",
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def render_term(term: str) -> str:
    definition = GLOSSARY.get(term, "")
    return f"<button type='button' class='term-btn' data-term='{esc(term)}' data-definition='{esc(definition)}'>{html.escape(term)}</button>"


def render_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\[(.+?)\]\((#.+?)\)", lambda m: f"<a href='{m.group(2)}'>{m.group(1)}</a>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", text).strip("-")
    return cleaned or "section"


def section_key(title: str) -> str:
    m = re.match(r"^(\d+(?:\.\d+)*)", title)
    if m:
        return m.group(1)
    m = re.match(r"^[（(][一二三四五六七八九十]+[)）]", title)
    if m:
        return m.group(0)
    return title


def formula_number(text: str) -> str | None:
    m = re.search(r"\((\d+(?:\.\d+)?)\)", text)
    return m.group(1) if m else None


def figure_number(text: str) -> int | None:
    m = re.search(r"图\s*([0-9]+)", text)
    if m:
        return int(m.group(1))
    return None


def parse_markdown(text: str) -> list[dict]:
    sections: list[dict] = []
    current = None
    lines = text.replace("\r\n", "\n").split("\n")
    i = 0

    def ensure_section(title: str, level: int) -> dict:
        nonlocal current
        section = {
            "title": title.strip(),
            "level": level,
            "id": slugify(f"{len(sections)+1}-{title}"),
            "blocks": [],
            "key": section_key(title.strip()),
        }
        sections.append(section)
        current = section
        return section

    def need_section() -> dict:
        nonlocal current
        if current is None:
            return ensure_section("导言", 2)
        return current

    def add_block(block: dict) -> None:
        need_section()["blocks"].append(block)

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            ensure_section(heading.group(2).strip(), len(heading.group(1)))
            i += 1
            continue

        if stripped.startswith("$$"):
            formula_lines = [stripped[2:]]
            i += 1
            while i < len(lines):
                candidate = lines[i].rstrip()
                if candidate.strip().endswith("$$"):
                    formula_lines.append(candidate.strip()[:-2])
                    break
                formula_lines.append(candidate)
                i += 1
            formula_body = "\n".join(part for part in formula_lines if part)
            equation_number = None
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if formula_number(next_line):
                    equation_number = formula_number(next_line)
                    i += 1
            add_block({"type": "formula", "latex": formula_body, "number": equation_number})
            i += 1
            continue

        image = re.match(r"^!\[.*?\]\((.+?)\)$", stripped)
        if image:
            add_block({"type": "image", "src": image.group(1).strip(), "caption": ""})
            i += 1
            continue

        anchor_caption = re.match(r"^<span id=\"([^\"]+)\"></span>(.*)$", stripped)
        if anchor_caption:
            anchor = anchor_caption.group(1)
            caption_text = anchor_caption.group(2).strip()
            blocks = need_section()["blocks"]
            if blocks and blocks[-1]["type"] == "image" and not blocks[-1].get("caption"):
                blocks[-1]["caption"] = caption_text
                blocks[-1]["anchor"] = anchor
            else:
                add_block({"type": "caption", "anchor": anchor, "text": caption_text})
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            add_block({"type": "table", "lines": table_lines})
            continue

        if stripped.startswith("- "):
            items = [stripped[2:].strip()]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            add_block({"type": "list", "items": items})
            continue

        para = [stripped]
        i += 1
        while i < len(lines):
            candidate = lines[i].strip()
            if not candidate:
                break
            if re.match(r"^(#{1,6})\s+", candidate) or candidate.startswith("$$") or candidate.startswith("!") or candidate.startswith("|") or candidate.startswith("- ") or candidate.startswith("<span id="):
                break
            para.append(candidate)
            i += 1
        add_block({"type": "paragraph", "text": " ".join(para)})

    return sections


def render_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        parts = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if parts and all(set(part) <= {"-", ":"} for part in parts):
            continue
        rows.append(parts)
    if not rows:
        return ""
    head = rows[0]
    body = rows[1:]
    thead = "<tr>" + "".join(f"<th>{render_inline(cell)}</th>" for cell in head) + "</tr>"
    tbody = "".join("<tr>" + "".join(f"<td>{render_inline(cell)}</td>" for cell in row) + "</tr>" for row in body)
    return f"<div class='table-wrap'><table><thead>{thead}</thead><tbody>{tbody}</tbody></table></div>"


def render_block(block: dict) -> str:
    if block["type"] == "paragraph":
        return f"<p>{render_inline(block['text'])}</p>"
    if block["type"] == "list":
        items = "".join(f"<li>{render_inline(item)}</li>" for item in block["items"])
        return f"<ul>{items}</ul>"
    if block["type"] == "table":
        return render_table(block["lines"])
    if block["type"] == "formula":
        number = f"<div class='formula-no'>({block['number']})</div>" if block.get("number") else ""
        button = f"<button type='button' class='latex-copy' data-latex='{esc(block['latex'])}'>复制 LaTeX</button>"
        return (
            "<div class='formula-card'>"
            f"<div class='formula-toolbar'>{button}{number}</div>"
            f"<div class='formula-display'>\\[{block['latex']}\\]</div>"
            "</div>"
        )
    if block["type"] == "image":
        src = f"marker-assets/{Path(block['src']).name}"
        caption = block.get("caption", "")
        anchor = f" id='{esc(block['anchor'])}'" if block.get("anchor") else ""
        figure_html = (
            f"<figure class='paper-figure'{anchor}>"
            f"<img src='{src}' alt='{esc(caption or Path(block['src']).name)}'>"
            f"<figcaption>{render_inline(caption)}</figcaption>"
            "</figure>"
        )
        number = figure_number(caption)
        if number and number in FIGURE_NOTES:
            note = FIGURE_NOTES[number]
            figure_html += f"<details class='figure-note'><summary>图解</summary><p>{render_inline(note)}</p></details>"
        return figure_html
    if block["type"] == "caption":
        anchor = f" id='{esc(block['anchor'])}'" if block.get("anchor") else ""
        return f"<p class='caption-only'{anchor}>{render_inline(block['text'])}</p>"
    return ""


def render_notes(section: dict) -> str:
    notes = SECTION_NOTES.get(section["key"], None)
    if not notes:
        return "<div class='note-card'><div class='note-head'>这一节</div><p>这一节保留原文抽取结果，便于对照正文、公式和图表。</p></div>"
    cards = []
    for label, body in notes.items():
        cards.append(
            "<div class='note-card'>"
            f"<div class='note-head'>{html.escape(label)}</div>"
            f"<p>{render_inline(body)}</p>"
            "</div>"
        )
    return "".join(cards)


def render_section(section: dict) -> str:
    blocks_html = "".join(render_block(block) for block in section["blocks"])
    return (
        f"<section class='reading-row' id='{section['id']}'>"
        "<div class='original-col'>"
        f"<div class='section-kicker'>原文抽取</div><h2>{render_inline(section['title'])}</h2>"
        f"<div class='paper-flow'>{blocks_html}</div>"
        "</div>"
        "<aside class='note-col'>"
        f"<div class='section-kicker'>带读</div>{render_notes(section)}"
        "</aside>"
        "</section>"
    )


def render_summary() -> str:
    cards = []
    for title, body in SUMMARY_CARDS:
        cards.append(
            "<article class='summary-card'>"
            f"<h3>{html.escape(title)}</h3>"
            f"<p>{render_inline(body)}</p>"
            "</article>"
        )
    return "".join(cards)


def render_glossary() -> str:
    buttons = "".join(render_term(term) for term in GLOSSARY)
    return f"<div class='glossary-panel'><div class='glossary-title'>术语</div><div class='glossary-list'>{buttons}</div></div>"


def render_toc(sections: list[dict]) -> str:
    links = [f"<a href='#{section['id']}'>{render_inline(section['title'])}</a>" for section in sections]
    return "".join(links)


def build_html(sections: list[dict]) -> str:
    toc = render_toc(sections)
    summary = render_summary()
    glossary = render_glossary()
    sections_html = "".join(render_section(section) for section in sections)
    pdf_link = PDF_REL
    return f"""<!DOCTYPE html>
<html lang='zh-CN'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>时频域干扰抑制算法 | paper-reading-html rerun</title>
  <script>
    window.MathJax={{tex:{{inlineMath:[['$','$'],['\\(','\\)']],displayMath:[['$$','$$'],['\\[','\\]']]}},options:{{skipHtmlTags:['script','noscript','style','textarea','pre']}}}};
  </script>
  <script defer src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js'></script>
  <style>
    :root {{
      --bg: #f4efe4;
      --paper: #fffdf8;
      --ink: #1e1e1b;
      --muted: #635d52;
      --line: #d8cfbf;
      --accent: #8e5a2b;
      --accent-soft: #efe4d2;
      --note: #f8f1e6;
      --shadow: 0 18px 40px rgba(57, 43, 23, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "PingFang SC", "Microsoft YaHei", sans-serif; background: linear-gradient(180deg, #efe6d5 0%, var(--bg) 28%, #f8f3eb 100%); color: var(--ink); }}
    a {{ color: inherit; }}
    .topbar {{ position: sticky; top: 0; z-index: 30; backdrop-filter: blur(12px); background: rgba(248, 243, 235, 0.9); border-bottom: 1px solid rgba(141, 114, 78, 0.18); }}
    .topbar-inner {{ max-width: 1480px; margin: 0 auto; padding: 14px 24px; display: flex; gap: 24px; align-items: center; justify-content: space-between; }}
    .brand {{ font-size: 14px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); font-weight: 700; }}
    .meta {{ display: flex; gap: 18px; align-items: center; color: var(--muted); font-size: 14px; flex-wrap: wrap; }}
    .meta a {{ text-decoration: none; padding: 8px 12px; border: 1px solid var(--line); border-radius: 999px; background: var(--paper); }}
    .shell {{ max-width: 1480px; margin: 0 auto; padding: 28px 24px 56px; }}
    .hero {{ display: grid; grid-template-columns: minmax(0, 1.4fr) 360px; gap: 24px; align-items: stretch; margin-bottom: 24px; }}
    .hero-main, .hero-side {{ background: rgba(255,253,248,0.86); border: 1px solid rgba(142, 90, 43, 0.14); border-radius: 24px; box-shadow: var(--shadow); }}
    .hero-main {{ padding: 28px; }}
    .hero-kicker {{ margin: 0 0 8px; color: var(--accent); font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }}
    h1 {{ margin: 0 0 14px; font-size: clamp(30px, 5vw, 54px); line-height: 1.05; }}
    .hero-main p {{ color: var(--muted); line-height: 1.8; }}
    .hero-preview {{ width: 100%; height: 100%; object-fit: cover; border-radius: 24px 24px 0 0; display: block; }}
    .hero-side-copy {{ padding: 18px 20px 22px; }}
    .hero-side h2 {{ margin: 0 0 10px; font-size: 20px; }}
    .layout {{ display: grid; grid-template-columns: 260px minmax(0, 1fr); gap: 24px; }}
    .rail {{ position: sticky; top: 88px; align-self: start; display: grid; gap: 18px; }}
    .rail-card {{ background: rgba(255,253,248,0.9); border: 1px solid rgba(142,90,43,0.14); border-radius: 20px; padding: 18px; box-shadow: var(--shadow); }}
    .rail-card h3 {{ margin: 0 0 12px; font-size: 16px; }}
    .toc a {{ display: block; text-decoration: none; color: var(--muted); padding: 8px 0; border-top: 1px solid rgba(216,207,191,0.7); }}
    .toc a:first-child {{ border-top: 0; padding-top: 0; }}
    .main {{ display: grid; gap: 26px; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 18px; }}
    .summary-card {{ background: rgba(255,253,248,0.92); border: 1px solid rgba(142,90,43,0.14); border-radius: 22px; padding: 22px; box-shadow: var(--shadow); }}
    .summary-card h3 {{ margin: 0 0 10px; font-size: 18px; }}
    .summary-card p {{ margin: 0; color: var(--muted); line-height: 1.8; }}
    .reading-row {{ display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(280px, 0.85fr); gap: 22px; align-items: start; }}
    .original-col, .note-col {{ background: rgba(255,253,248,0.92); border: 1px solid rgba(142,90,43,0.14); border-radius: 24px; box-shadow: var(--shadow); }}
    .original-col {{ padding: 24px; }}
    .note-col {{ padding: 20px; position: sticky; top: 88px; }}
    .section-kicker {{ color: var(--accent); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; }}
    .original-col h2 {{ margin: 0 0 16px; font-size: 28px; }}
    .paper-flow {{ color: var(--ink); }}
    .paper-flow p, .paper-flow li {{ line-height: 1.9; color: #2d2a24; }}
    .paper-flow ul {{ padding-left: 22px; margin: 10px 0 18px; }}
    .paper-flow a {{ color: var(--accent); }}
    .paper-figure {{ margin: 18px 0 12px; padding: 16px; background: #fbf6ec; border: 1px solid #eadfcd; border-radius: 18px; }}
    .paper-figure img {{ width: 100%; border-radius: 12px; display: block; background: white; }}
    .paper-figure figcaption {{ margin-top: 10px; color: var(--muted); line-height: 1.75; }}
    .caption-only {{ color: var(--muted); font-size: 14px; }}
    .figure-note {{ margin: 0 0 18px; border: 1px dashed #d1b48f; border-radius: 16px; background: #fff6ea; padding: 0 14px; }}
    .figure-note summary {{ cursor: pointer; padding: 12px 0; color: var(--accent); font-weight: 700; }}
    .figure-note p {{ margin: 0 0 14px; color: var(--muted); }}
    .formula-card {{ margin: 18px 0; padding: 16px 18px; border-radius: 18px; background: #fbf6ec; border: 1px solid #eadfcd; }}
    .formula-toolbar {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 8px; }}
    .formula-no {{ color: var(--muted); font-size: 14px; }}
    .latex-copy {{ border: 1px solid #d5c0a5; background: white; border-radius: 999px; padding: 8px 12px; cursor: pointer; }}
    .formula-display {{ overflow-x: auto; padding: 4px 0; }}
    .table-wrap {{ overflow-x: auto; margin: 18px 0; border: 1px solid #eadfcd; border-radius: 16px; background: #fbf6ec; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 420px; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #eadfcd; text-align: left; line-height: 1.6; }}
    th {{ background: #f4ead9; }}
    .note-card {{ padding: 16px 18px; border-radius: 18px; background: var(--note); border: 1px solid #eadfcd; margin-bottom: 14px; }}
    .note-head {{ color: var(--accent); font-size: 13px; font-weight: 700; margin-bottom: 8px; }}
    .note-card p {{ margin: 0; line-height: 1.8; color: var(--muted); }}
    .glossary-panel {{ display: grid; gap: 12px; }}
    .glossary-title {{ font-size: 16px; font-weight: 700; }}
    .glossary-list {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .term-btn {{ border: 1px solid #d5c0a5; background: white; border-radius: 999px; padding: 8px 12px; cursor: pointer; font: inherit; }}
    .term-pop {{ position: fixed; right: 24px; bottom: 24px; width: min(360px, calc(100vw - 32px)); background: rgba(34,31,26,0.96); color: white; border-radius: 18px; padding: 18px; box-shadow: 0 24px 48px rgba(0,0,0,0.24); display: none; z-index: 40; }}
    .term-pop.show {{ display: block; }}
    .term-pop h4 {{ margin: 0 0 8px; font-size: 18px; }}
    .term-pop p {{ margin: 0; line-height: 1.7; color: rgba(255,255,255,0.84); }}
    .close-pop {{ margin-top: 12px; border: 1px solid rgba(255,255,255,0.24); background: transparent; color: white; border-radius: 999px; padding: 6px 12px; cursor: pointer; }}
    @media (max-width: 1120px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .rail {{ position: static; }}
      .reading-row {{ grid-template-columns: 1fr; }}
      .note-col {{ position: static; }}
      .summary-grid {{ grid-template-columns: 1fr; }}
      .hero {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header class='topbar'>
    <div class='topbar-inner'>
      <div>
        <div class='brand'>paper-reading-html rerun</div>
        <div class='meta'>
          <span>第一篇重跑</span>
          <span>原文抽取 + 结构带读</span>
          <a href='{pdf_link}'>原 PDF</a>
        </div>
      </div>
    </div>
  </header>
  <main class='shell'>
    <section class='hero'>
      <div class='hero-main'>
        <p class='hero-kicker'>时频域干扰抑制算法</p>
        <h1>第一篇重跑预览</h1>
        <p>这一版直接接入 <strong>Marker 原文抽取</strong> 的正文、图片和可读公式，把原文带读和文档解读重新放回一个页面里。当前优先恢复的是 <strong>可读性</strong>、<strong>公式复制</strong> 和 <strong>图片就地解读</strong>，让你先能顺着整篇文章读下来。</p>
        <p>如果只抓全文脉络，这篇文章的中心其实很清楚：<strong>频域解决窄带和单音干扰，时域解决高斯脉冲干扰，最后统一用 BER 回退判断值不值得</strong>。</p>
      </div>
      <div class='hero-side'>
        <img class='hero-preview' src='{PREVIEW_REL}' alt='第一页预览'>
        <div class='hero-side-copy'>
          <h2>文档解读</h2>
          <p>下面的第一大板块是 <strong>原文带读</strong>，第二大板块是 <strong>文档解读</strong>。原文里保留图片和公式，右侧则用结构化带读卡片帮你抓每一节到底在做什么。</p>
        </div>
      </div>
    </section>
    <div class='layout'>
      <aside class='rail'>
        <div class='rail-card'>
          <h3>目录</h3>
          <nav class='toc'>{toc}</nav>
        </div>
        <div class='rail-card'>{glossary}</div>
      </aside>
      <section class='main'>
        <section class='summary-grid'>
          {summary}
        </section>
        {sections_html}
      </section>
    </div>
  </main>
  <div class='term-pop' id='term-pop'>
    <h4 id='term-title'>术语</h4>
    <p id='term-body'></p>
    <button type='button' class='close-pop' id='close-pop'>关闭</button>
  </div>
  <script>
    document.querySelectorAll('.latex-copy').forEach((button) => {{
      button.addEventListener('click', async () => {{
        const value = button.getAttribute('data-latex') || '';
        try {{
          await navigator.clipboard.writeText(value);
          button.textContent = '已复制';
          setTimeout(() => button.textContent = '复制 LaTeX', 1200);
        }} catch (error) {{
          button.textContent = '复制失败';
          setTimeout(() => button.textContent = '复制 LaTeX', 1200);
        }}
      }});
    }});
    const pop = document.getElementById('term-pop');
    const title = document.getElementById('term-title');
    const body = document.getElementById('term-body');
    document.querySelectorAll('.term-btn').forEach((button) => {{
      button.addEventListener('click', () => {{
        title.textContent = button.getAttribute('data-term') || '术语';
        body.textContent = button.getAttribute('data-definition') || '暂无解释';
        pop.classList.add('show');
      }});
    }});
    document.getElementById('close-pop').addEventListener('click', () => pop.classList.remove('show'));
  </script>
</body>
</html>
"""



FLOW_FIGURES = {19, 20, 21, 30, 32}
FIGURE_META = {
    19: {"focus": "频域总流程", "axes": "这类流程图没有 x/y 轴，要看模块先后", "series": "接收数据 -> 频域检测 -> 频域抑制 -> 后续链路", "trend": "从左到右形成完整闭环", "reason": "作者先拆检测，再拆抑制，方便后面逐项调参", "claim": "频域方案是一条完整处理链"},
    20: {"focus": "重叠加窗流程", "axes": "没有坐标轴，重点看加窗和 FFT 的顺序", "series": "Hanning 窗、1/2 重叠、频域检测、抑制连起来", "trend": "先稳住频谱，再谈门限", "reason": "不先压住泄漏，后面的检测会漂", "claim": "加窗是检测前置条件"},
    21: {"focus": "CME 与 FCME 对比", "axes": "没有坐标轴，重点看背景集合怎样初始化", "series": "CME 先假定全体样点干净，FCME 先信任低能样点", "trend": "两法框架相近，分歧集中在起点", "reason": "初始化方式不同，后续复杂度也不同", "claim": "两法差在初始化，不在总框架"},
    22: {"focus": "漏检概率对比", "axes": "横轴 JNR / dB，纵轴 漏检概率", "series": "CME 与 FCME 两条曲线", "trend": "JNR 增大时两条曲线都下降，而且彼此接近", "reason": "两法同属能量检测框架", "claim": "FCME 没拿出明显更低的漏检率优势"},
    23: {"focus": "虚警概率对比", "axes": "横轴 JNR / dB，纵轴 虚警概率", "series": "CME 与 FCME 两条曲线", "trend": "曲线仍然接近，没有明显分离", "reason": "虚警最终仍由同一套门限逻辑主导", "claim": "作者有理由优先选复杂度更低的 CME"},
    24: {"focus": "平滑前后的频域幅度谱", "axes": "横轴 频点 / 子载波位置，纵轴 频域幅度", "series": "不同滑动因子下的多幅频谱图", "trend": "未平滑时起伏大，平滑后更连贯；窗口过大又会抹宽", "reason": "局部平均压住波动，也会把能量拖到邻频", "claim": "平滑有用，但不能过强"},
    25: {"focus": "滑动因子与漏检概率", "axes": "横轴 JNR / dB，纵轴 漏检概率", "series": "不同滑动因子 theta 的多条曲线", "trend": "过小和过大的滑动因子都不好，中间区间最稳", "reason": "窗口太小平滑不够，太大又会摊薄边缘", "claim": "0.005 到 0.01 左右是更稳的参数区"},
    26: {"focus": "不同带宽下的漏检概率", "axes": "横轴 JNR / dB，纵轴 漏检概率", "series": "不同窄带干扰带宽的多条曲线", "trend": "JNR 越高越容易检测；带宽越宽越难检测", "reason": "总功率分到更多频点后，每个频点不够突出", "claim": "方法更适合局部集中干扰"},
    27: {"focus": "单音干扰抑制前后", "axes": "横轴 频点 / 频率位置，纵轴 频域幅度", "series": "(a) 抑制前，(b) 抑制后", "trend": "目标频点尖峰被直接压成凹陷", "reason": "单音干扰高度集中，最容易检测和置零对位", "claim": "频域置零能精准命中单频干扰"},
    28: {"focus": "5% 窄带干扰抑制前后", "axes": "横轴 频点 / 频率位置，纵轴 频域幅度", "series": "(a) 抑制前，(b) 抑制后", "trend": "干扰带被整体压成一段凹陷", "reason": "平滑后整段干扰仍足够突出", "claim": "方法能抓住连续窄带"},
    29: {"focus": "10% 窄带干扰抑制前后", "axes": "横轴 频点 / 频率位置，纵轴 频域幅度", "series": "(a) 抑制前，(b) 抑制后", "trend": "凹陷更宽，连带损失更明显", "reason": "带宽变宽后，被切掉的频点自然更多", "claim": "方法仍有效，但代价已经抬头"},
    30: {"focus": "频域性能仿真流程", "axes": "没有坐标轴，重点看 BER 怎样从整条链路算出来", "series": "信号生成、加干扰、检测、抑制、译码、BER 统计", "trend": "把检测和抑制重新放回完整通信链路", "reason": "波形图好看不代表链路一定恢复", "claim": "后面的 BER 曲线建立在完整流程上"},
    31: {"focus": "频域抑制后的 BER 曲线", "axes": "横轴 SNR / dB，纵轴 BER", "series": "无干扰与不同干扰带宽的多条曲线", "trend": "所有曲线都下降，但带宽越大整体越往右上偏", "reason": "带宽越大，置零牺牲的有效频点越多", "claim": "1%、5%、10% 带宽下回退仍控制在 1dB 内"},
    32: {"focus": "时域总流程", "axes": "没有坐标轴，重点看样点如何直接进入检测与抑制", "series": "时域样点 -> 检测 -> 样点置零 -> 后续链路", "trend": "不再先做 FFT，而是直接在时域定位脉冲", "reason": "脉冲干扰在时域位置上本来就很突出", "claim": "时域路线把观测对象从频点换成了样点"},
    33: {"focus": "时域平滑前后对比", "axes": "横轴 时间样点，纵轴 时域幅度", "series": "两种占空比下，平滑前后四幅波形图", "trend": "平滑后脉冲包络更稳，和噪声更容易分开", "reason": "局部平均压住了随机尖峰波动", "claim": "时域检测同样依赖平滑来稳门限"},
    34: {"focus": "不同占空比下的漏检概率", "axes": "横轴 JNR / dB，纵轴 漏检概率", "series": "不同占空比 gamma_j 的多条曲线", "trend": "同一 JNR 下，占空比越大漏检越高", "reason": "占空比增大后，脉冲不再像稀疏异常点", "claim": "整段检测对小占空比更友好"},
    35: {"focus": "不同分段长度下的漏检概率", "axes": "横轴 JNR / dB，纵轴 漏检概率", "series": "不同分段长度的多条曲线", "trend": "分段长度会改变曲线的下降速度和稳定性", "reason": "太短会出现空段，太长又会混入过多背景样点", "claim": "分段长度接近干扰周期时更优"},
    36: {"focus": "时域脉冲抑制前后", "axes": "横轴 时间样点，纵轴 时域幅度", "series": "(a) 抑制前，(b) 抑制后", "trend": "高幅脉冲被切掉后形成周期性凹陷", "reason": "时域置零直接打在检测出的脉冲位置上", "claim": "时域置零命中位置，但也会留下时间凹陷"},
    37: {"focus": "不同占空比下的 BER 性能", "axes": "横轴 SNR / dB，纵轴 BER；含整段检测和分段检测两块", "series": "不同占空比与无干扰参考曲线", "trend": "占空比越大 BER 越差，分段检测侧通常更靠下", "reason": "分段窗口更贴近干扰周期，统计更对位", "claim": "10% 占空比以内两法都可用，但分段更有余量"},
}
FORMULA_META = {
    "3.1": ("把虚警概率换成门限因子", "$P_f$ 控制容忍的误报水平，$T$ 决定门限高低", "它把“门限怎么设”落实成可算表达式", "这不是结果式，而是检测性格的调参式"),
    "3.2": ("定义漏检概率", "$S$ 是仿真次数，$b_m(j)$ 是每次漏掉的样点数", "后面的漏检曲线都按这套口径来算", "记住它定义了图 22、25、26 的纵轴"),
    "3.3": ("定义频域平滑", "$L$ 是窗口半宽，$\\widehat{Y}(l)$ 是平滑后的幅度", "它把“为什么要平滑”变成“如何平滑”", "它本质上是局部平均器"),
    "3.4": ("定义频域置零规则", "$I$ 是受干扰频点集合，$\\hat Y(k)$ 是处理后结果", "检测模块给出集合，这里把集合变成动作", "优点是直接，代价是有用频点也会被一起切掉"),
    "3.5": ("定义时域接收信号模型", "$x(t)$ 有用信号，$h(t)$ 信道，$n(t)$ 噪声，$I_j(t)$ 脉冲干扰", "它把后面的占空比与周期参数全部引出来", "真正的新项是脉冲干扰那一项"),
    "3.6": ("重写时域抑制阶段的接收模型", "$w(t)$ 噪声，$J_\\varrho(t)$ 时域高斯脉冲干扰", "它给后面的时域置零做符号准备", "作用是钉牢抑制前的对象"),
    "3.7": ("定义时域置零规则", "$I$ 是受污染样点集合", "它和式 (3.4) 的思路完全对应，只是对象换成时域样点", "成败几乎完全取决于前面的检测是否够准"),
}

OLD_BUILD_HTML = build_html

def clean_heading(title: str) -> str:
    title = re.sub(r'<span id="[^"]+"></span>', '', title)
    title = title.replace('**', '')
    return re.sub(r'\s+', ' ', title).strip()


def extract_formula_no(block: dict) -> str | None:
    if block.get('number'):
        m = re.search(r'([0-9]+(?:\.[0-9]+)?)', block['number'])
        if m:
            return m.group(1)
    m = re.search(r'\\tag\{([^}]+)\}', block.get('latex', ''))
    if m:
        n = re.search(r'([0-9]+(?:\.[0-9]+)?)', m.group(1))
        if n:
            return n.group(1)
    return None


def strip_formula_tag(latex: str) -> str:
    return re.sub(r'\\tag\{[^}]+\}', '', latex).strip()


def section_thread_rows(title: str) -> list[tuple[str, str]]:
    t = clean_heading(title)
    if '1.1.1' in t:
        return [('问题', '怎样在频域里既看见干扰，又别误伤太多有用频点。'), ('盯住', '加窗、门限、平滑、CME/FCME。'), ('收口', '后面的置零能不能有效，取决于这里先找得准不准。')]
    if '1.1.2' in t:
        return [('问题', '把已检出的受扰频点直接变成置零操作。'), ('盯住', '凹陷位置是否对位，代价是否开始扩散。'), ('收口', '这里看的不是算法名，而是切得准不准。')]
    if '1.1.3' in t:
        return [('问题', '波形图看着干净以后，BER 到底回来了多少。'), ('盯住', '曲线整体右移量，而不是只看是否下降。'), ('收口', '只有 BER 回收，前面的检测和置零才算值。')]
    if '1.2.1' in t:
        return [('问题', '脉冲干扰怎样建模，以及整段检测和分段检测差在哪里。'), ('盯住', '平滑、占空比、分段长度。'), ('收口', '统计窗口怎么选，是这一节真正的核心。')]
    if '1.2.2' in t:
        return [('问题', '把检测出的脉冲样点怎样直接切掉。'), ('盯住', '是否只在脉冲位置留下凹陷。'), ('收口', '难点不在公式，在检测集合够不够准。')]
    if '1.2.3' in t:
        return [('问题', '整段检测和分段检测的 BER 谁更稳。'), ('盯住', '占空比增大时的曲线右移量。'), ('收口', '波形切对了还不够，链路要真的恢复。')]
    if '(一) 单音' in t:
        return [('问题', '单频干扰能否被精准命中。'), ('盯住', '第 300 个频点附近是否被准确切掉。'), ('收口', '这是整条频域链最干净的基线例子。')]
    if '(二) 窄带' in t:
        return [('问题', '干扰带宽变宽后，检测和平滑还能不能跟上。'), ('盯住', '带内凹陷是否完整，邻频损失是否抬头。'), ('收口', '这里开始出现方法代价。')]
    if '(一) 整段检测' in t:
        return [('问题', '不切段时，时域检测能做到什么程度。'), ('盯住', '占空比变大时为什么会越来越难。'), ('收口', '整段检测给分段检测提供参照。')]
    if '(二) 分段检测' in t:
        return [('问题', '分段长度怎样改变检测统计。'), ('盯住', '窗口是否贴近干扰周期。'), ('收口', '太短和太长都会坏。')]
    if '1.2' in t:
        return [('问题', '如果干扰是脉冲性的，该怎样在样点层面找和切。'), ('盯住', '周期、持续时间、占空比。'), ('收口', '时域路线把观测对象从频点换成了样点。')]
    if '1.1' in t:
        return [('问题', '窄带和单音干扰在频域里该怎样先检测再抑制。'), ('盯住', '流程图、门限、平滑、置零。'), ('收口', '后面所有参数都围着这条链打转。')]
    return [('问题', '先看这一节想解决什么问题。'), ('盯住', '它和上一节怎么接。'), ('收口', '再确认它最后落到哪张图或哪条公式。')]


def paragraph_rows(title: str, text: str) -> list[tuple[str, str]]:
    p = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', text.replace('**', '').replace('*', ''))).strip()
    if 'FFT' in p and '频谱泄露' in p:
        return [('作用', '解释为什么频域检测前必须先加窗。'), ('承接', '作者先把为什么能看清干扰说清楚。'), ('记住', '不先压住频谱泄漏，后面的门限就不稳。')]
    if 'Hanning' in p or '窗长' in p:
        return [('作用', '展开窗口类型与 FFT 长度的取舍。'), ('承接', '加窗必要性讲完，这里开始谈参数。'), ('记住', '这里讨论的是分辨率与复杂度交换。')]
    if '重叠加窗' in p or '1/2' in p:
        return [('作用', '说明为什么普通加窗还不够。'), ('承接', '作者承认加窗有副作用，再给出补偿。'), ('记住', '重叠加窗是在稳频谱，而不是做装饰。')]
    if '基于能量检测方法' in p and '频点' in p:
        return [('作用', '把 CME 和 FCME 的共同基础钉死。'), ('承接', '频谱形状稳住以后，才进入真正检测。'), ('记住', '方法成立的前提是干扰在频域里足够突出。')]
    if '核心思想是一致的' in p and 'FCME' in p:
        return [('作用', '拆开 CME 和 FCME 的差别。'), ('承接', '上一段只讲共性，这一段讲分歧。'), ('记住', '差别主要在背景集合初始化。')]
    if '门限因子 T' in p:
        return [('作用', '把图里的门限真正说清楚，并引到式 (3.1)。'), ('承接', '流程看懂后，作者补最关键的判决量。'), ('记住', '门限不是小参数，它决定误报和漏检平衡。')]
    if '虚警概率' in p and '门限因子' in p:
        return [('作用', '把门限表读成一个取舍问题。'), ('承接', '公式给出后，这段解释高门限和低门限各坏在哪。'), ('记住', '检测门限从来不是越保守越好。')]
    if 'P_m' in p and '漏检概率' in p:
        return [('作用', '定义后面多张检测曲线的纵轴。'), ('承接', '门限讲完，开始交代评价指标。'), ('记住', '图 22、25、26 的纵轴都来自这里。')]
    if '由图 22 和图 23' in p:
        return [('作用', '根据检测结果做算法取舍。'), ('承接', '先比较，再决策。'), ('记住', '作者选 CME 是因为性能接近但复杂度更低。')]
    if '频域幅值进行平滑处理' in p:
        return [('作用', '解释为什么还要再做一次平滑。'), ('承接', '算法选定以后，开始处理门限不稳的问题。'), ('记住', '平滑不是修图，而是在改检测统计量。')]
    if '图 24' in p and '平滑' in p:
        return [('作用', '把平滑效果翻译成能看见的频谱变化。'), ('承接', '公式给了算式，这里解释算式后果。'), ('记住', '平滑太小不够，太大又会抹宽干扰边缘。')]
    if p.startswith('以下是针对几种干扰类型'):
        return [('作用', '把频域检测部分收住，转入抑制效果展示。'), ('承接', '前面回答能不能检出来，这里开始看切得怎么样。'), ('记住', '关注点从门限转到凹陷位置和 BER。')]
    if '一个 OFDM 符号为 512 个子载波' in p:
        return [('作用', '钉住单音干扰实验参数。'), ('承接', '置零规则出来后，先看最简单基线。'), ('记住', '单音实验验证的是能不能精准命中一个点。')]
    if '由图 27' in p:
        return [('作用', '直接读图 27 的结果。'), ('承接', '参数给完后检查抑制是否对位。'), ('记住', '单音干扰被准确压在目标频点上。')]
    if '干扰带宽为 5%时' in p and '图 [28]' in p:
        return [('作用', '把单音升级成 5% 和 10% 两档带宽。'), ('承接', '从一点扩成一段连续频带。'), ('记住', '这里开始比较收益和代价何时一起抬头。')]
    if '由对比图可以看出' in p and '凹陷' in p:
        return [('作用', '概括图 28 和图 29 的共同结论。'), ('承接', '图放完以后，把视觉印象收成判断。'), ('记住', '平滑先连起干扰带，再由置零把整段压成凹陷。')]
    if '对单用户的 OFDM 链路在不同 SNR' in p:
        return [('作用', '交代 BER 比较口径并开始读图 31。'), ('承接', '完整流程给出后，正式看链路指标。'), ('记住', '带宽越大 BER 越差，但 1%、5%、10% 仍在 1dB 回退内。')]
    if '本节研究时域高斯脉冲干扰的检测与抑制' in p:
        return [('作用', '把问题从频域切到时域。'), ('承接', '上一大节讲完后，开始展开另一类干扰。'), ('记住', '这里不再先做 FFT，而是直接看样点。')]
    if p.startswith('时域脉冲干扰是一种比较典型的干扰'):
        return [('作用', '先把时域脉冲干扰的物理特征和模型写清楚。'), ('承接', '进入时域路线后，先定义异常长什么样。'), ('记住', '功率大、持续短，所以在时域里表现成少量高幅突起。')]
    if p.startswith('式中,h(t)为信道系数') or p.startswith('式中, x(t)'):
        return [('作用', '解释时域模型的符号，并把读者带到图 33。'), ('承接', '信号模型写出来后，开始说明为什么还要平滑。'), ('记住', '图 33 的重点不是好看，而是门限更稳。')]
    if p.startswith('由于时域脉冲干扰在整个时间维度上都存在'):
        return [('作用', '说明为什么要先拿整段检测做基线。'), ('承接', '图 33 之后，开始比较统计窗口。'), ('记住', '分段长度一旦选坏，统计集合本身就会被扭曲。')]
    if '图 [34]' in p and '干扰周期' in p:
        return [('作用', '固定整段检测的仿真口径。'), ('承接', '整段检测的理由说完，开始给图 34 的量化结果。'), ('记住', '图 34 主要观察占空比怎样改变漏检率。')]
    if p.startswith('虽然在接收端直接对带有高斯脉冲干扰的信号进行整段检测'):
        return [('作用', '说明为什么还要进一步尝试分段检测。'), ('承接', '整段检测先给参照，再转向更工程化的方法。'), ('记住', '分段首先是工程需要，其次才是性能机会。')]
    if '图 [35]' in p and '分段样点数' in p:
        return [('作用', '把分段检测的比较对象固定下来。'), ('承接', '分段动机讲完后，开始真正比较不同窗口。'), ('记住', '关键不是绝对长度，而是它和干扰周期的相对位置。')]
    if p.startswith('针对时域高斯脉冲干扰,常用的干扰抑制方法有置零') or p.startswith('针对时域高斯脉冲干扰,常用的干扰抑制方法有置零和限幅'):
        return [('作用', '解释为什么时域抑制最后还是选置零。'), ('承接', '前面比较的是怎样找，现在开始决定怎样切。'), ('记住', '限幅压高度，置零才是真正把干扰拿掉。')]
    if p.startswith('式中,I 是在时域干扰检测中得到的受到干扰'):
        return [('作用', '补上时域置零最脆弱的地方。'), ('承接', '公式给出后，作者说明它最依赖什么。'), ('记住', '难点不在置零，而在集合 I 够不够准。')]
    if p.startswith('本节将对前文提到的时域干扰检测与抑制算法'):
        return [('作用', '正式把时域方案拉到 BER 指标上。'), ('承接', '波形图看完后，开始看链路指标。'), ('记住', '最终裁判仍然是 BER。')]
    if p.startswith('首先对时域高斯脉冲干扰采用整段检测的方法'):
        return [('作用', '先解释图 37(a) 的整段检测 BER 曲线。'), ('承接', '总口径交代后，先给整段检测基线。'), ('记住', '占空比越大，BER 回退越重。')]
    if p.startswith('然后采用分段检测的方法对时域高斯脉冲干扰进行干扰检测与抑制仿真'):
        return [('作用', '再解释图 37(b) 的分段检测 BER 曲线。'), ('承接', '整段基线给出后，开始比较分段是否更稳。'), ('记住', '分段检测在较大占空比时通常更有优势。')]
    if p.startswith('将整段检测和分段检测的仿真结果图进行对比可知'):
        return [('作用', '把整段检测和分段检测做最终并排比较。'), ('承接', '两张 BER 子图都读完后，这里给时域路线收口。'), ('记住', '10% 占空比以内两法都可用，但分段更有余量。')]
    return [('作用', f'这段在当前小节里继续推进论证：{p[:32]}'), ('承接', f'它接在 {clean_heading(title)} 这节下面，继续往图、公式或结论推进。'), ('记住', '不要只记字面意思，记它在整条方法链里卡在哪一步。')]


def list_rows(items: list[str]) -> list[tuple[str, str]]:
    t = ' '.join(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', x.replace('**', '').replace('*', ''))).strip() for x in items)
    if '0.005 ~ 0.01' in t or '0.005~0.01' in t:
        return [('作用', '把图 25 的曲线结论翻译成参数建议。'), ('承接', '前面先让你看见平滑效果，这里再把它量化。'), ('记住', '滑动因子过小和过大都不好，中间区间更稳。')]
    if '40%带宽之内' in t or '50%时' in t:
        return [('作用', '把图 26 的多条带宽曲线收成判断。'), ('承接', '它把带宽与漏检率的关系说透。'), ('记住', '频域路线更适合局部集中干扰。')]
    if '0.03~0.05' in t and '占空比' in t:
        return [('作用', '把图 34 的多条占空比曲线收成判断。'), ('承接', '整段检测结果到这里才真正变成边界。'), ('记住', '小占空比是整段检测的舒适区。')]
    if '分段长度等于 1000' in t or '5000、10000' in t:
        return [('作用', '把图 35 的多条分段长度曲线收成判断。'), ('承接', '真正的比较不是谁绝对最小，而是谁更贴近周期。'), ('记住', '太短和太长都会坏，贴近干扰周期最好。')]
    return [('作用', '这组条目是在把图后的观察整理成判断。'), ('承接', '它通常跟在主图之后，负责把视觉印象变成结论。'), ('记住', '不要只记数字，记它最后支持的是哪一个参数判断。')]


def table_rows(lines: list[str]) -> list[tuple[str, str]]:
    header = ' | '.join(c.strip() for c in lines[0].strip('|').split('|'))
    if '虚警概率' in header:
        return [('作用', '把式 (3.1) 的结果整理成门限查表。'), ('承接', '公式给出后，表格把抽象关系压成可用参数。'), ('记住', '虚警概率越小，门限因子越大。')]
    return [('作用', '把后面曲线比较真正变化的参数列清楚。'), ('承接', '图上的差别不是凭感觉，而是按固定口径比出来的。'), ('记住', '先看哪些量被固定，再看哪些量被拿来对比。')]


def figure_rows(caption: str) -> list[tuple[str, str]]:
    num = figure_number(caption or '')
    meta = FIGURE_META.get(num)
    if not meta:
        return [('作用', '这是从原 PDF 抽出的局部图块。'), ('承接', '若没有完整图号，先把它当作相邻主图的辅助局部。'), ('记住', '主判断以下方有完整图号和图注的图片为准。')]
    return [('图里看什么', meta['focus']), ('坐标 / 结构', meta['axes']), ('变量 / 曲线', meta['series']), ('趋势 / 结构变化', meta['trend']), ('为什么会这样', meta['reason']), ('这图说明什么', meta['claim'])]


def formula_rows(block: dict) -> list[tuple[str, str]]:
    num = extract_formula_no(block)
    meta = FORMULA_META.get(num)
    if not meta:
        return [('作用', '这条公式是当前推导里的关键节点。'), ('承接', '它把上一段文字收成可计算表达式。'), ('记住', '抓住它输入什么、输出什么、卡在哪一步。')]
    return [('作用', meta[0]), ('关键变量', meta[1]), ('前后衔接', meta[2]), ('读完要记住', meta[3])]


def note_card_html(head: str, rows: list[tuple[str, str]]) -> str:
    body = ''.join(f"<p><strong>{html.escape(k)}</strong> {render_inline(v)}</p>" for k, v in rows)
    return f"<div class='note-card'><div class='note-head'>{html.escape(head)}</div>{body}</div>"


def render_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r'\[(.+?)\]\((#.+?)\)', lambda m: f"<a href='{m.group(2)}'>{m.group(1)}</a>", text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text.replace('&lt;sup&gt;', '<sup>').replace('&lt;/sup&gt;', '</sup>').replace('&lt;sub&gt;', '<sub>').replace('&lt;/sub&gt;', '</sub>')


def parse_markdown(text: str) -> list[dict]:
    sections, current = [], None
    lines = text.replace('\r\n', '\n').split('\n')
    i = 0
    def ensure(title, level):
        nonlocal current
        current = {'title': title.strip(), 'level': level, 'id': slugify(f"{len(sections)+1}-{clean_heading(title)}"), 'blocks': [], 'key': clean_heading(title)}
        sections.append(current)
        return current
    def need():
        nonlocal current
        return current or ensure('导言', 2)
    def add(block):
        need()['blocks'].append(block)
    def attach(anchor, caption):
        blocks = need()['blocks']
        if blocks and blocks[-1]['type'] == 'image' and not blocks[-1].get('caption'):
            blocks[-1]['caption'] = caption
            if anchor:
                blocks[-1]['anchor'] = anchor
        else:
            add({'type': 'caption', 'text': caption, 'anchor': anchor})
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        h = re.match(r'^(#{1,6})\s+(.*)$', s)
        if h:
            title = h.group(2).strip()
            clean = clean_heading(title)
            if re.match(r'^图\s*[0-9]+', clean):
                m = re.match(r'^<span id="([^"]+)"></span>(.*)$', title)
                attach(m.group(1) if m else None, clean_heading(m.group(2) if m else title))
            elif re.match(r'^由图\s*[0-9]+', clean):
                add({'type': 'subheading', 'text': clean})
            else:
                ensure(title, len(h.group(1)))
            i += 1
            continue
        if s.startswith('<span id='):
            m = re.match(r'^<span id="([^"]+)"></span>(.*)$', s)
            attach(m.group(1) if m else None, clean_heading(m.group(2) if m else s))
            i += 1
            continue
        img = re.match(r'^!\[.*?\]\((.+?)\)$', s)
        if img:
            add({'type': 'image', 'src': img.group(1).strip(), 'caption': ''})
            i += 1
            continue
        if s.startswith('$$'):
            parts = []
            if s != '$$':
                first = s[2:]
                if first.endswith('$$'):
                    parts.append(first[:-2]); i += 1
                else:
                    parts.append(first); i += 1
                    while i < len(lines):
                        c = lines[i].rstrip()
                        if c.strip().endswith('$$'):
                            parts.append(c.strip()[:-2]); i += 1; break
                        parts.append(c); i += 1
            else:
                i += 1
                while i < len(lines):
                    c = lines[i].rstrip()
                    if c.strip().endswith('$$'):
                        parts.append(c.strip()[:-2]); i += 1; break
                    parts.append(c); i += 1
            latex = '\n'.join(p for p in parts if p).strip()
            latex = re.sub(r'\\tag\{[^}]+\}', '', latex).strip()
            num = (re.match(r'^\\(([0-9]+(?:\\.[0-9]+)?)\\)$', lines[i].strip()).group(1) if i < len(lines) and re.match(r'^\\(([0-9]+(?:\\.[0-9]+)?)\\)$', lines[i].strip()) else None)
            if num: i += 1
            add({'type': 'formula', 'latex': latex, 'number': num})
            continue
        if s.startswith('|'):
            table = [s]; i += 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                table.append(lines[i].strip()); i += 1
            add({'type': 'table', 'lines': table}); continue
        if s.startswith('- '):
            items = [s[2:].strip()]; i += 1
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append(lines[i].strip()[2:].strip()); i += 1
            add({'type': 'list', 'items': items}); continue
        para = [s]; i += 1
        while i < len(lines):
            c = lines[i].strip()
            if not c or re.match(r'^(#{1,6})\s+', c) or c.startswith('$$') or c.startswith('!') or c.startswith('|') or c.startswith('- ') or c.startswith('<span id='):
                break
            para.append(c); i += 1
        add({'type': 'paragraph', 'text': ' '.join(para)})
    out = []
    for sec in sections:
        key = clean_heading(sec['title'])
        if (re.match(r'^图\s*[0-9]+', key) or re.match(r'^由图\s*[0-9]+', key)) and out:
            out[-1]['blocks'].extend(sec['blocks']); continue
        sec['key'] = key; out.append(sec)
    return out


def render_block(block: dict) -> str:
    if block['type'] == 'paragraph':
        return f"<p>{render_inline(block['text'])}</p>"
    if block['type'] == 'list':
        items = ''.join(f"<li>{render_inline(item)}</li>" for item in block['items'])
        return f"<ul>{items}</ul>"
    if block['type'] == 'table':
        return render_table(block['lines'])
    if block['type'] == 'formula':
        latex = strip_formula_tag(block['latex'])
        number = extract_formula_no(block)
        number_html = f"<div class='formula-no'>({number})</div>" if number else ''
        button = f"<button type='button' class='latex-copy' data-latex='{esc(latex)}'>复制 LaTeX</button>"
        return "<div class='formula-card'>" f"<div class='formula-toolbar'>{button}{number_html}</div>" f"<div class='formula-display'>\\[{html.escape(latex)}\\]</div></div>"
    if block['type'] == 'image':
        src = f"marker-assets/{Path(block['src']).name}"
        caption = block.get('caption', '')
        anchor = f" id='{esc(block['anchor'])}'" if block.get('anchor') else ''
        return f"<figure class='paper-figure'{anchor}><img src='{src}' alt='{esc(caption or Path(block['src']).name)}'><figcaption>{render_inline(caption)}</figcaption></figure>"
    if block['type'] == 'caption':
        anchor = f" id='{esc(block['anchor'])}'" if block.get('anchor') else ''
        return f"<p class='caption-only'{anchor}>{render_inline(block['text'])}</p>"
    if block['type'] == 'subheading':
        return f"<div class='note-card'><div class='note-head'>{render_inline(block['text'])}</div><p>下面进入对上一张图的集中解读，这不是新的主章节，而是图后总结入口。</p></div>"
    return ''


def render_notes(section: dict) -> str:
    cards = [note_card_html('这一节', section_thread_rows(section['title']))]
    p = l = t = 0
    for block in section['blocks']:
        if block['type'] == 'paragraph':
            p += 1; cards.append(note_card_html(f'P{p}', paragraph_rows(section['title'], block['text'])))
        elif block['type'] == 'list':
            l += 1; cards.append(note_card_html(f'L{l}', list_rows(block['items'])))
        elif block['type'] == 'table':
            t += 1; cards.append(note_card_html(f'T{t}', table_rows(block['lines'])))
        elif block['type'] == 'formula':
            num = extract_formula_no(block)
            cards.append(note_card_html(f'式 ({num})' if num else '公式', formula_rows(block)))
        elif block['type'] == 'image':
            num = figure_number(block.get('caption', ''))
            cards.append(note_card_html(f'图 {num}' if num else '配图', figure_rows(block.get('caption', ''))))
    return ''.join(cards)
# == detailed note overrides ==
FORMULA_META.update({
    '3.4': ('给出频域置零的执行规则', '$I$ 是被判为受干扰的频点集合，$\\hat Y(k)$ 是抑制后的频谱', '检测小节先把受污染频点找出来，这里把检测结果真正变成抑制动作', '这条式子说明作者选的是直接切除，不是估计补偿'),
    '3.5': ('写出含脉冲干扰的时域接收模型', '$x(t)$ 是发送信号，$h(t)$ 是信道，$n(t)$ 是噪声，$I_j(t)$ 是脉冲干扰', '先把时域问题写成统一模型，后面才能讨论周期、持续时间和占空比', '重点不是推导复杂，而是把干扰项单独拎出来')
})

PARAGRAPH_NOTE_ROWS = {
    '1 基带干扰检测与抑制技术及性能': {
        1: [('这段在说什么', '先把全文拆成两条线: 频域处理单音和窄带干扰，时域处理高斯脉冲干扰。'), ('和上下文怎么接', '这是整章入口，后面所有流程图、检测曲线和 BER 曲线都归到这两条线里。'), ('读完要记住', '不要把这章看成零散算法，要看成两条完整的抗干扰链。')],
    },
    '1.1 频域干扰检测与抑制技术': {
        1: [('这段在说什么', '先说明频域抗干扰为什么必须放在接收前端做，因为干扰会先破坏同步和译码。'), ('和上下文怎么接', '总章节刚把全文分成频域和时域两条线，这一段正式展开频域路线，并把图 19 当成总导航。'), ('读完要记住', '后面所有门限、平滑和置零，其实都在围着图 19 这条频域链路打转。')],
    },
    '1.1.1 频域干扰检测技术': {
        1: [('这段在说什么', '先解释为什么频域检测前必须加窗: 不加窗直接做 FFT，会产生频谱泄漏，干扰会溢到邻近频点。'), ('和上下文怎么接', '作者没有立刻讲 CME，而是先把“怎样看清干扰”这个前提处理说清楚。'), ('读完要记住', '频域检测的第一步不是设门限，而是先把频谱形状稳住。')],
        2: [('这段在说什么', '这一段把窗函数类型和 FFT 长度的取舍展开了: 要让干扰能量更集中，也要控制计算量。'), ('和上下文怎么接', '上段讲加窗必要性，这里开始把“用什么窗、窗长多大”落成可实现参数。'), ('读完要记住', '1024 点窗长不是随手给的，它对应的是分辨率和复杂度之间的折中。')],
        3: [('这段在说什么', '这里承认普通加窗本身也有代价，比如信号畸变和能量损失，所以作者再引入 1/2 重叠加窗做补偿。'), ('和上下文怎么接', '前两段先说为什么要加窗，这一段继续把副作用和补救办法一起交代清楚。'), ('读完要记住', '重叠加窗不是装饰步骤，它是在尽量保住频谱可判性。')],
        4: [('这段在说什么', '这一段把 CME 和 FCME 的共同基础钉死了: 都是能量检测，本质上都在找能量异常的频点。'), ('和上下文怎么接', '频谱前处理讲完以后，论文才进入真正的检测算法层。'), ('读完要记住', '这两种算法能成立，前提是干扰在频域里足够尖锐、足够突出。')],
        5: [('这段在说什么', '这里把 CME 和 FCME 的差别拆开: 不是判决准则不同，而是背景集合的初始化方式不同。'), ('和上下文怎么接', '上一段先讲两法的共同地基，这一段才讲两法真正分叉的地方。'), ('读完要记住', 'CME 默认大多数样点先干净，FCME 先信低能样点，这个起点差异会带来复杂度差异。')],
        6: [('这段在说什么', '这一段把图 21 里的门限真正写成式 (3.1)，说明门限因子 T 决定检测有多保守。'), ('和上下文怎么接', '流程图看懂后，作者补上最关键的判决量，让检测从流程变成可算表达式。'), ('读完要记住', '门限因子不是小参数，它直接控制误报和漏检的平衡点。')],
        7: [('这段在说什么', '这里先点明式 (3.1) 里的核心变量: 预设虚警概率 $P_f$ 不同，对应的门限因子也不同。'), ('和上下文怎么接', '公式刚写出来，这一段开始把抽象符号转成能查、能调的参数表。'), ('读完要记住', '$P_f$ 不是附属参数，它决定门限高低，也决定后面检得太松还是太紧。')],
        8: [('这段在说什么', '这一段把表 4 读成一个取舍问题: 虚警概率设太小，门限太高，会漏掉干扰；设太大，门限太低，会误伤有用频点。'), ('和上下文怎么接', '前一段只是把表引出来，这一段才告诉你表里的数字该怎样理解。'), ('读完要记住', '检测门限没有“越保守越好”这回事，真正重要的是漏检和虚警一起看。')],
        9: [('这段在说什么', '这里给出漏检概率的定义式 (3.2)，目的是给后面所有检测曲线统一一个评价指标。'), ('和上下文怎么接', '门限设定讲完后，论文立刻转去回答: 这套检测到底好不好，该用什么指标量化。'), ('读完要记住', '图 22、图 25、图 26 的纵轴都建立在这条漏检概率定义上。')],
        10: [('这段在说什么', '这一段把式 (3.2) 里的变量解释清楚，并交代图 22 和图 23 的仿真口径: 固定 10% 窄带干扰，同场比较 CME 和 FCME。'), ('和上下文怎么接', '评价指标刚定义完，这里马上进入第一次算法对比实验。'), ('读完要记住', '作者不是抽象地说 CME、FCME 谁好，而是把它们放到同一组 JNR 条件下比较漏检和虚警。')],
        11: [('这段在说什么', '这里给出第一次明确决策: 两种算法性能接近，但 FCME 复杂度更高，所以全文后续统一选 CME。'), ('和上下文怎么接', '前面的图 22 和图 23 不是摆证据，而是为这里的算法取舍服务。'), ('读完要记住', '作者选 CME 的理由是“够用且更省”，这是很工程化的判断。')],
        12: [('这段在说什么', '这一段开始讨论为什么仅靠 CME 还不够: 复高斯窄带干扰会让频域幅值起伏很大，所以还要先做平滑。'), ('和上下文怎么接', '算法选定以后，论文接着处理检测统计量不稳定的问题，并引到式 (3.3)。'), ('读完要记住', '平滑不是后处理美化，而是在直接改变检测输入的统计形态。')],
        13: [('这段在说什么', '这里把图 24 的四幅频谱图读成一个规律: 平滑越强，曲线越顺，但干扰带边缘也会被抹宽。'), ('和上下文怎么接', '上一段先给出平滑公式，这一段解释那个公式在图上到底带来了什么变化。'), ('读完要记住', '平滑的价值是拉开干扰与噪声，代价是把干扰能量抹到邻频。')],
        14: [('这段在说什么', '这一段正式进入图 25 的参数扫描: 固定 10% 带宽，只改变滑动因子，看漏检概率怎样变。'), ('和上下文怎么接', '图 24 还只是视觉对比，这里开始把“平滑因子选多大”变成定量判断。'), ('读完要记住', '作者想找的不是某条单独最好曲线，而是一段更稳、更不容易翻车的参数区间。')],
        15: [('这段在说什么', '这一段把研究对象从滑动因子换成干扰带宽: 固定平滑因子 0.01，比较不同窄带宽度下的漏检概率。'), ('和上下文怎么接', '滑动因子范围定下来以后，论文继续追问这套检测方法到底能扛多宽的干扰。'), ('读完要记住', '这里真正要回答的是频域路线的适用边界，而不只是再画一张曲线图。')],
    },
    '1.1.2 频域干扰抑制技术': {
        1: [('这段在说什么', '这里把检测结果真正变成抑制动作: 一旦频点被判进集合 $I$，就直接置零。'), ('和上下文怎么接', '前一节回答“找不找得到”，这一节开始回答“找到了以后怎么切”。'), ('读完要记住', '作者选的是最直接的置零策略，优点是干脆，代价是会同时损失这些频点上的有用信息。')],
        2: [('这段在说什么', '这一句是频域抑制部分的过渡句，告诉你下面不再讲公式，而是直接看不同干扰类型的抑制效果。'), ('和上下文怎么接', '置零规则给出后，论文立刻把它放到单音和窄带两种场景里验证。'), ('读完要记住', '后面看图时不要只看有没有压下去，还要看凹陷有没有扩太宽。')],
    },
    '(一) 单音干扰抑制': {
        1: [('这段在说什么', '这一段把单音干扰实验口径交代清楚: 子载波数、采样率、干扰频点和 JNR 都被固定，目的是看能否精准命中一个点。'), ('和上下文怎么接', '频域抑制先从最简单的单音干扰开始，相当于先测这把刀够不够准。'), ('读完要记住', '单音实验的核心不是“压低多少”，而是“能不能只切该切的那个频点”。')],
        2: [('这段在说什么', '这一段直接解读图 27: 300 号附近的尖峰被明显压下，说明检测点和置零点对上了。'), ('和上下文怎么接', '参数交代完以后，论文立刻回到图上验证抑制动作有没有打准位置。'), ('读完要记住', '单音场景里，置零的优势是精准；如果连这里都压不准，后面宽带情况更不可能做好。')],
    },
    '(二) 窄带干扰抑制': {
        1: [('这段在说什么', '这一段把窄带干扰实验分成 5% 和 10% 两档，目的是看从“一个频点”扩成“一段频带”以后，置零还能不能跟得上。'), ('和上下文怎么接', '单音只是最简单基线，这里才开始面对连续受污染频带。'), ('读完要记住', '从这一段开始，评价标准不再只是打得准，还要看整段频带能不能连贯切除。')],
        2: [('这段在说什么', '这里把图 28 和图 29 合在一起收成一句话: 平滑先把窄带干扰带连起来，置零再把整段压成凹陷。'), ('和上下文怎么接', '上段给实验设置，这一段才把 5% 和 10% 两档结果真正读出来。'), ('读完要记住', '带宽一变宽，凹陷也会一起变宽，频域抑制的副作用会开始抬头。')],
    },
    '1.1.3 性能仿真分析': {
        1: [('这段在说什么', '这一段把前面分开的检测和抑制重新串回完整链路，并用图 30 和图 31 把 BER 仿真的上下文搭起来。'), ('和上下文怎么接', '前面频域部分一直在讲局部图形，这里第一次把裁判标准换成整条通信链路的 BER。'), ('读完要记住', '真正的收口不在单张频谱图，而在抑制后系统误码率有没有回来。')],
        2: [('这段在说什么', '这里直接读图 31 的 BER 曲线: SNR 上升时所有曲线都下降，但干扰带宽越大，曲线整体越往右移。'), ('和上下文怎么接', '完整流程图给出后，作者开始用同一条链路比较不同带宽的干扰代价。'), ('读完要记住', '频域路线对局部窄带干扰有效，但干扰带一变宽，BER 回退就会越来越明显。')],
        3: [('这段在说什么', '这一句把图 31 的关键定量结论收住了: 1%、5%、10% 这几档窄带干扰下，达到相同 BER 所需的 SNR 回退都还控制在 1dB 以内。'), ('和上下文怎么接', '长段曲线解释后，这里用一个最关键的量化结果给频域路线收口。'), ('读完要记住', '在本文的目标场景里，10% 以内的窄带干扰仍然属于这套方法的舒适区。')],
    },
    '1.2 时域干扰检测与抑制技术': {
        1: [('这段在说什么', '这里把全文主线从频域切到时域: 仍然沿用 CME 检测和置零抑制，但对象从频点换成时域样点。'), ('和上下文怎么接', '频域部分已经回答了单音和窄带问题，现在轮到高斯脉冲干扰。'), ('读完要记住', '同样叫检测和置零，频域损失的是子载波，时域损失的是时间连续性。')],
    },
    '1.2.1 时域干扰检测技术': {
        1: [('这段在说什么', '这一段先把时域脉冲干扰的物理特征和接收模型摆出来: 干扰功率大、持续时间短，所以会在样点上冒出尖峰。'), ('和上下文怎么接', '切到时域路线后，作者先回答“异常在时域里长什么样”。'), ('读完要记住', '式 (3.5) 的价值不是复杂推导，而是把脉冲干扰单独拎成一个显式项。')],
        2: [('这段在说什么', '这里解释式 (3.5) 里的几个关键参数，尤其是周期、持续时间和占空比，它们决定后面图 34 和图 37 的横向比较口径。'), ('和上下文怎么接', '模型刚写出来，这一段立刻把符号翻成能做实验、能画曲线的物理量。'), ('读完要记住', '时域部分最重要的控制量不是带宽，而是周期和占空比。')],
        3: [('这段在说什么', '这一段说明时域里为什么也要平滑，并把图 33 读成“平滑前后脉冲与背景分离度”的对比。'), ('和上下文怎么接', '参数定义完后，作者开始处理和频域相同的问题: 样点起伏太大，门限不稳。'), ('读完要记住', '时域平滑的目的不是把波形变漂亮，而是让脉冲样点和噪声底分得更开。')],
        4: [('这段在说什么', '这一段把时域检测正式拆成整段检测和分段检测两条路。'), ('和上下文怎么接', '图 33 说明平滑有效之后，论文开始讨论统计窗口该怎样取。'), ('读完要记住', '后面真正要比较的不是有没有检测，而是整段统计和分段统计谁更适合脉冲干扰。')],
    },
    '(一) 整段检测': {
        1: [('这段在说什么', '这里先说明为什么要把整段检测当基线: 当干扰周期未知或占空比偏大时，贸然分段可能直接把统计集合切坏。'), ('和上下文怎么接', '上一段刚把时域检测分成两条路，这里先展开较稳妥的整段检测。'), ('读完要记住', '整段检测的价值不是最优，而是先给一个不依赖周期对齐的参照系。')],
        2: [('这段在说什么', '这一段给出图 34 的仿真口径: 固定 CME、滑动因子和门限，只改变占空比，看漏检概率怎样变化。'), ('和上下文怎么接', '整段检测的动机讲完后，论文立刻把它放进参数扫描实验。'), ('读完要记住', '图 34 真正要观察的是占空比怎样改变检测难度。')],
        3: [('这段在说什么', '这一段解释图 34 背后的原因: 总干扰功率一定时，占空比越大，单个脉冲样点就越不突出，所以更难检出来。'), ('和上下文怎么接', '前面的列表把实验现象列出来，这里把现象背后的统计原因说透。'), ('读完要记住', '整段检测更喜欢低占空比、稀疏突出的脉冲。')],
    },
    '(二) 分段检测': {
        1: [('这段在说什么', '这里说明为什么还要研究分段检测: 一帧太长时，整段处理的计算和硬件代价都很高。'), ('和上下文怎么接', '整段检测先给出性能基线，这里转向更接近工程实现的方法。'), ('读完要记住', '分段最初是工程需要，但窗口一旦选对，也可能反过来提升检测性能。')],
        2: [('这段在说什么', '这一段把图 35 的比较口径钉住了: 固定占空比 0.05，只改分段长度，看哪种长度和干扰周期更匹配。'), ('和上下文怎么接', '分段动机讲完后，论文开始比较不同窗口长度怎样改变检测统计。'), ('读完要记住', '这里真正比较的不是绝对长度，而是分段长度和干扰周期的相对关系。')],
    },
    '1.2.2 时域干扰抑制技术': {
        1: [('这段在说什么', '这一段先把限幅和置零做了取舍: 面对强脉冲干扰，限幅只能压高，不能真正去掉干扰，所以最后还是选置零。'), ('和上下文怎么接', '前面一直在讨论怎样把脉冲找出来，这里开始决定找到以后怎样处理。'), ('读完要记住', '时域部分和频域部分一样，都选择了最直接的切除策略。')],
        2: [('这段在说什么', '这里把时域接收信号重新写成式 (3.6)，目的是在抑制小节里把“原始接收信号里有什么”重新摆清楚。'), ('和上下文怎么接', '决定采用置零后，作者先把要处理的对象写成标准模型。'), ('读完要记住', '这条式子是在给下一步的置零规则搭舞台。')],
        3: [('这段在说什么', '这一段解释式 (3.6) 里的各个分量，并把叙述顺势引到式 (3.7) 的置零规则。'), ('和上下文怎么接', '接收模型摆齐以后，论文立即回答置零到底怎样作用到这个模型上。'), ('读完要记住', '从这里开始，核心不再是信号表达式，而是集合 $I$ 到底准不准。')],
        4: [('这段在说什么', '这里把时域置零最脆弱的地方说出来了: 门限和集合 $I$ 选得不好，就会在抑制干扰和保留信号之间失衡。'), ('和上下文怎么接', '式 (3.7) 给出之后，这一段补上它成立的前提条件。'), ('读完要记住', '置零本身不复杂，真正难的是检测阶段要把脉冲位置圈准。')],
        5: [('这段在说什么', '这一段把图 36 的仿真场景交代清楚: 固定周期、占空比和 JSR，专门看抑制前后的时域波形差异。'), ('和上下文怎么接', '置零原理说完后，作者先不急着看 BER，而是先回到波形层面确认有没有打准位置。'), ('读完要记住', '图 36 的任务是验证置零动作本身，而不是验证整条链路极限性能。')],
        6: [('这段在说什么', '这一段直接读图 36: 抑制前是周期性高幅脉冲，抑制后同样位置出现周期性凹陷，两者一一对应。'), ('和上下文怎么接', '仿真参数给完后，作者回到图上检验置零是否真的命中了干扰所在样点。'), ('读完要记住', '时域置零能打准脉冲位置，但它留下的凹陷本身也是一种代价。')],
    },
    '1.2.3 性能仿真分析': {
        1: [('这段在说什么', '这一段把时域检测和抑制重新拉回 BER 指标，说明最终仍然要用整条链路的误码率来裁判。'), ('和上下文怎么接', '波形图已经证明置零能打中位置，这里开始看打中以后链路到底恢复了多少。'), ('读完要记住', '时域部分的最终收口也不在波形，而在 BER 曲线。')],
        2: [('这段在说什么', '这里先布置图 37(a) 的整段检测实验: 固定 JSR 和周期，只改变占空比，观察 BER 曲线怎样右移。'), ('和上下文怎么接', '总口径交代完以后，作者先给出整段检测这条基线。'), ('读完要记住', '图 37(a) 的任务是给后面的分段检测一个可比较的参照。')],
        3: [('这段在说什么', '这一段把图 37(a) 的结果读细了: 占空比越大，BER 曲线越往右移，10% 占空比时回退已经明显增大。'), ('和上下文怎么接', '实验设置给完后，这里第一次把整段检测的 BER 代价量化出来。'), ('读完要记住', '整段检测在低占空比时还能接受，占空比一大，链路回退就会明显抬头。')],
        4: [('这段在说什么', '这里开始布置图 37(b) 的分段检测实验，保持同样的干扰强度和占空比范围，只把检测方式换成分段。'), ('和上下文怎么接', '整段检测的 BER 基线给出后，论文开始看分段以后是否能把损失再收回来一点。'), ('读完要记住', '这一段最关键的不是参数复述，而是“其余条件尽量不变，只改检测方式”。')],
        5: [('这段在说什么', '这一段直接读图 37(b): 分段检测下 BER 同样随 SNR 下降，但在较大占空比时，曲线通常比整段检测更靠左。'), ('和上下文怎么接', '实验设置刚交代完，这里马上把分段检测的实际收益量化出来。'), ('读完要记住', '分段检测不是所有情况下都压倒性更强，但在较大占空比时更有余量。')],
        6: [('这段在说什么', '这一段把图 37 的两块子图并排比较，给出时域路线的最终判断: 10% 占空比以内两法都可用，但分段检测更稳。'), ('和上下文怎么接', '整段和分段两组 BER 曲线都读完后，这里给时域部分收口。'), ('读完要记住', '作者最后留下来的不是万能算法，而是一条带着适用边界的工程结论。')],
    },
}

LIST_NOTE_ROWS = {
    '1.1.1 频域干扰检测技术': {
        1: [('这组条目在收什么', '这是把图 25 的多条滑动因子曲线收成参数建议，核心是在找“既不漏太多，也不扩散太多”的区间。'), ('和上文怎么接', '前面图 24 还只是看波形变化，这里开始把平滑因子真正变成可选参数。'), ('读完要记住', '0.005 到 0.01 这一段更稳，太小不够平滑，太大又会把干扰抹宽。')],
        2: [('这组条目在收什么', '这是把图 26 的多条带宽曲线收成适用边界，告诉你频域检测对多宽的窄带干扰还算有效。'), ('和上文怎么接', '滑动因子范围确定后，这里继续问方法本身的工作边界在哪里。'), ('读完要记住', '频域路线对 20% 以内的局部窄带干扰最舒服，带宽再变宽，漏检会明显增加。')],
    },
    '(一) 整段检测': {
        1: [('这组条目在收什么', '这是把图 34 的多条占空比曲线收成一句判断: 占空比越大，整段检测越吃力。'), ('和上文怎么接', '图已经画出趋势，这组条目把趋势翻译成检测边界。'), ('读完要记住', '整段检测更适合低占空比、稀疏突出的脉冲。')],
    },
    '(二) 分段检测': {
        1: [('这组条目在收什么', '这是把图 35 的多条分段长度曲线收成一个窗口选择原则。'), ('和上文怎么接', '前面只给实验设置，这组条目才真正把不同分段长度的优劣说透。'), ('读完要记住', '分段长度太短会出现空段，太长又会把背景均值拉低，贴近干扰周期时最合适。')],
    },
}

TABLE_NOTE_ROWS = {
    '1.1.1 频域干扰检测技术': {
        1: [('这张表在做什么', '把式 (3.1) 的抽象关系压成一张可直接查值的门限表。'), ('和上文怎么接', '公式给出后，这张表把虚警概率和门限因子的对应关系落成工程参数。'), ('读完要记住', '虚警概率越小，门限因子越大，检测会更保守。')],
    },
}

FIGURE_NOTE_ROWS = {
    19: [('横轴', '无。流程图按左到右读，表示处理顺序。'), ('纵轴', '无。上下模块表示不同处理环节。'), ('变量 / 对象', '接收数据、频域检测、频域抑制、后续接收链路。'), ('趋势 / 结构', '从前端检测一路走到抑制，再回到系统链路。'), ('为什么会这样', '作者先把检测和抑制拆成模块，后面才能分别讨论门限、平滑和置零。'), ('这图说明什么', '频域抗干扰不是单一步骤，而是一条完整处理链。')],
    20: [('横轴', '无。流程图按先后顺序看。'), ('纵轴', '无。上下分支只是模块展开。'), ('变量 / 对象', 'Hanning 窗、1/2 重叠、FFT、检测、抑制。'), ('趋势 / 结构', '先加窗稳频谱，再做检测，再把受干扰频点切掉。'), ('为什么会这样', '如果不先压住频谱泄漏，后面的能量门限会跟着漂。'), ('这图说明什么', '重叠加窗是频域检测的前置处理，不是可有可无的修饰。')],
    21: [('横轴', '无。两张子图都是流程结构图。'), ('纵轴', '无。主要看步骤顺序和集合更新方式。'), ('变量 / 对象', 'CME 的全体初始化方式，FCME 的排序后初始化方式。'), ('趋势 / 结构', '两条流程框架相近，但起点不同。'), ('为什么会这样', '两者都想估计干净背景，只是对“谁先算干净样点”的假设不同。'), ('这图说明什么', 'CME 和 FCME 的差异主要在背景集合初始化，而不是检测思想本身。')],
    22: [('横轴', 'JNR / dB。'), ('纵轴', '漏检概率。'), ('变量 / 对象', 'CME 和 FCME 两条检测曲线。'), ('趋势 / 结构', '随着 JNR 增大，两条曲线都下降，而且彼此非常接近。'), ('为什么会这样', '两种算法都基于能量检测，面对同一组 10% 窄带干扰时，检测能力差别不大。'), ('这图说明什么', '从漏检角度看，FCME 并没有明显拉开 CME。')],
    23: [('横轴', 'JNR / dB。'), ('纵轴', '虚警概率。'), ('变量 / 对象', 'CME 和 FCME 两条虚警曲线。'), ('趋势 / 结构', '两条曲线整体接近，没有出现一方显著更低的情况。'), ('为什么会这样', '两法的判决门限逻辑接近，差别主要在初始化，并没有把虚警性能明显拉开。'), ('这图说明什么', '把图 22 和图 23 合起来看，作者才有理由选择复杂度更低的 CME。')],
    24: [('横轴', '频率位置 / 频点序号。'), ('纵轴', '频域幅度。'), ('变量 / 对象', '未平滑与不同滑动因子的四幅频谱图。'), ('趋势 / 结构', '滑动因子越大，曲线越平滑，但受干扰频带边缘也越宽。'), ('为什么会这样', '滑动平均会压小局部起伏，同时把能量向邻近频点扩散。'), ('这图说明什么', '平滑有用，但只能取中等强度，过强会开始误伤邻频。')],
    25: [('横轴', 'JNR / dB。'), ('纵轴', '漏检概率。'), ('变量 / 对象', '不同滑动因子的多条检测曲线。'), ('趋势 / 结构', '中间一段滑动因子下降更稳，过小或过大的曲线都更高。'), ('为什么会这样', '过小不能压住幅值波动，过大会把干扰边缘稀释掉。'), ('这图说明什么', '滑动因子存在可工作的稳定区间，而不是越大越好。')],
    26: [('横轴', 'JNR / dB。'), ('纵轴', '漏检概率。'), ('变量 / 对象', '不同窄带宽度对应的多条曲线。'), ('趋势 / 结构', '带宽越窄，曲线下降越快；带宽越宽，在同样 JNR 下漏检越多。'), ('为什么会这样', '总干扰功率固定时，带宽一增大，分摊到每个频点上的能量就更不突出。'), ('这图说明什么', '频域检测更擅长局部集中干扰，对很宽的窄带干扰会逐渐吃力。')],
    27: [('横轴', '频点序号。'), ('纵轴', '频域幅度。'), ('变量 / 对象', '(a) 抑制前的单音尖峰，(b) 抑制后的频谱。'), ('趋势 / 结构', '300 号附近的尖峰被压下，抑制后对应位置形成局部凹陷。'), ('为什么会这样', '检测先锁定了单个异常频点，置零再直接把那个频点切掉。'), ('这图说明什么', '单音干扰场景下，频域置零可以做到较准确的点状命中。')],
    28: [('横轴', '频点序号。'), ('纵轴', '频域幅度。'), ('变量 / 对象', '5% 窄带干扰抑制前后的频谱对比。'), ('趋势 / 结构', '原来的一段受污染频带被整体压成连续凹陷，而不是只切最高峰。'), ('为什么会这样', '平滑先把窄带干扰带连成整体，置零才能按频带范围切除。'), ('这图说明什么', '5% 窄带时，频域抑制既能压下干扰，又没有把凹陷扩得太宽。')],
    29: [('横轴', '频点序号。'), ('纵轴', '频域幅度。'), ('变量 / 对象', '10% 窄带干扰抑制前后的频谱对比。'), ('趋势 / 结构', '凹陷明显比图 28 更宽，说明被切掉的频带范围更大。'), ('为什么会这样', '干扰带本来就更宽，置零时不可避免地会一起损失更多有效频点。'), ('这图说明什么', '带宽一增大，频域置零的副作用就会同步抬头。')],
    30: [('横轴', '无。流程图按左到右读。'), ('纵轴', '无。上下模块表示链路中的不同功能块。'), ('变量 / 对象', '编码、交织、OFDM、加干扰、检测抑制、解调译码。'), ('趋势 / 结构', '从发送端到接收端，干扰被插入，再被检测和抑制。'), ('为什么会这样', '作者要证明后面的 BER 结果来自完整链路，而不是孤立的小实验。'), ('这图说明什么', '图 31 的 BER 曲线是建立在整条频域抗干扰链路上的系统级结果。')],
    31: [('横轴', 'SNR / dB。'), ('纵轴', 'BER。'), ('变量 / 对象', '无干扰参考曲线，以及不同窄带带宽下的多条 BER 曲线。'), ('趋势 / 结构', 'SNR 增大时所有曲线都下降；带宽越大，曲线整体越往右移。'), ('为什么会这样', '带宽更大的窄带干扰会污染更多子载波，置零后也会损失更多有效信息。'), ('这图说明什么', '频域方案对 10% 以内窄带干扰仍然有效，但带宽继续增大时链路代价会变重。')],
    32: [('横轴', '无。流程图按左到右读。'), ('纵轴', '无。上下模块表示检测和抑制环节。'), ('变量 / 对象', '时域信号、CME 检测、置零抑制、后续链路。'), ('趋势 / 结构', '对象从频点变成时域样点，但总体仍然是检测先行、抑制随后。'), ('为什么会这样', '高斯脉冲干扰在时域更显眼，所以作者直接在样点域完成检测和切除。'), ('这图说明什么', '时域路线和频域路线结构相似，只是观测域和损失形式不同。')],
    33: [('横轴', '时间样点。'), ('纵轴', '时域幅度。'), ('变量 / 对象', '占空比 0.08 和 0.3 下，平滑前后的四幅波形图。'), ('趋势 / 结构', '平滑后脉冲包络更连贯，脉冲与背景噪声的幅度分离更明显。'), ('为什么会这样', '平滑压小了随机起伏，让真正的脉冲结构从噪声底里站出来。'), ('这图说明什么', '时域检测也需要平滑，尤其是在脉冲样点波动较大时。')],
    34: [('横轴', 'JNR / dB。'), ('纵轴', '漏检概率。'), ('变量 / 对象', '不同占空比对应的多条整段检测曲线。'), ('趋势 / 结构', '占空比越大，曲线越高；JNR 越大，曲线整体往下掉。'), ('为什么会这样', '总干扰功率固定时，占空比越大，单个脉冲样点就越不突出，越像背景。'), ('这图说明什么', '整段检测对低占空比脉冲更友好，占空比一大就更容易漏检。')],
    35: [('横轴', 'JNR / dB。'), ('纵轴', '漏检概率。'), ('变量 / 对象', '不同分段长度下的多条检测曲线。'), ('趋势 / 结构', '不同分段长度会改变曲线的下降速度和稳定性，贴近周期的窗口更稳。'), ('为什么会这样', '窗口太短会出现大量空段，窗口太长又会把背景均值拉低，都会破坏门限判决。'), ('这图说明什么', '分段长度不是越大越好，关键是和干扰周期对齐。')],
    36: [('横轴', '时间样点。'), ('纵轴', '时域幅度。'), ('变量 / 对象', '(a) 抑制前的脉冲波形，(b) 抑制后的时域波形。'), ('趋势 / 结构', '原来的周期性高幅脉冲被切掉后，在相同位置留下周期性凹陷。'), ('为什么会这样', '时域置零直接打在检测出的脉冲样点上，所以位置一一对应。'), ('这图说明什么', '时域置零能命中脉冲位置，但会把这些时间样点一起挖空。')],
    37: [('横轴', 'SNR / dB。'), ('纵轴', 'BER。'), ('变量 / 对象', '无干扰参考曲线，以及不同占空比下的整段检测和分段检测 BER 曲线。'), ('趋势 / 结构', '占空比越大，曲线越往右移；分段检测那一组通常比整段检测更靠左一些。'), ('为什么会这样', '分段窗口更容易贴近干扰周期，检测集合更准，后续置零带来的链路损失也更可控。'), ('这图说明什么', '10% 占空比以内两种方法都可用，但分段检测通常更有余量。')],
}

_BASE_PARAGRAPH_ROWS = paragraph_rows
_BASE_LIST_ROWS = list_rows
_BASE_TABLE_ROWS = table_rows
_BASE_FIGURE_ROWS = figure_rows


def _plain_note_text(text: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', text.replace('**', '').replace('*', ''))).strip()


def _skip_note_paragraph(text: str) -> bool:
    plain = _plain_note_text(text)
    if not plain:
        return True
    if re.fullmatch(r'\(?\s*\d+(?:\.\d+)?\s*\)?', plain):
        return True
    if re.match(r'^表\s*\d+\b', plain) and len(plain) <= 32:
        return True
    if plain.endswith('可知:') and len(plain) <= 20:
        return True
    return False


def _formula_no_from_context(blocks: list[dict], idx: int, block: dict) -> str | None:
    num = extract_formula_no(block)
    if num:
        return num
    if idx + 1 < len(blocks) and blocks[idx + 1]['type'] == 'paragraph':
        m = re.fullmatch(r'\(?\s*(\d+(?:\.\d+)?)\s*\)?', _plain_note_text(blocks[idx + 1]['text']))
        if m:
            return m.group(1)
    return None


def paragraph_rows(title: str, text: str, order: int | None = None) -> list[tuple[str, str]]:
    key = clean_heading(title)
    rows = PARAGRAPH_NOTE_ROWS.get(key, {}).get(order)
    if rows:
        return rows
    return _BASE_PARAGRAPH_ROWS(title, text)


def list_rows(title: str, items: list[str], order: int | None = None) -> list[tuple[str, str]]:
    key = clean_heading(title)
    rows = LIST_NOTE_ROWS.get(key, {}).get(order)
    if rows:
        return rows
    return _BASE_LIST_ROWS(items)


def table_rows(title: str, lines: list[str], order: int | None = None) -> list[tuple[str, str]]:
    key = clean_heading(title)
    rows = TABLE_NOTE_ROWS.get(key, {}).get(order)
    if rows:
        return rows
    return _BASE_TABLE_ROWS(lines)


def figure_rows(caption: str) -> list[tuple[str, str]]:
    num = figure_number(caption or '')
    rows = FIGURE_NOTE_ROWS.get(num)
    if rows:
        return rows
    return _BASE_FIGURE_ROWS(caption)


def render_notes(section: dict) -> str:
    cards = [note_card_html('这一节', section_thread_rows(section['title']))]
    p = l = t = 0
    blocks = section['blocks']
    for idx, block in enumerate(blocks):
        if block['type'] == 'paragraph':
            if _skip_note_paragraph(block['text']):
                continue
            p += 1
            cards.append(note_card_html(f'P{p}', paragraph_rows(section['title'], block['text'], p)))
        elif block['type'] == 'list':
            l += 1
            cards.append(note_card_html(f'L{l}', list_rows(section['title'], block['items'], l)))
        elif block['type'] == 'table':
            t += 1
            cards.append(note_card_html(f'T{t}', table_rows(section['title'], block['lines'], t)))
        elif block['type'] == 'formula':
            num = _formula_no_from_context(blocks, idx, block)
            block_with_num = dict(block)
            if num:
                block_with_num['number'] = num
            cards.append(note_card_html(f'式 ({num})' if num else '公式', formula_rows(block_with_num)))
        elif block['type'] == 'image':
            num = figure_number(block.get('caption', ''))
            if not num and not block.get('caption', '').strip():
                continue
            cards.append(note_card_html(f'图 {num}' if num else '配图', figure_rows(block.get('caption', ''))))
    return ''.join(cards)

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUT_HTML.exists():
        shutil.copy2(OUTPUT_HTML, LEGACY_HTML)
    for image in MARKER_DIR.glob("_page_*.*"):
        shutil.copy2(image, ASSET_DIR / image.name)
    text = MARKDOWN_PATH.read_text(encoding="utf-8")
    sections = parse_markdown(text)
    html_text = build_html(sections)
    OUTPUT_HTML.write_text(html_text, encoding="utf-8")
    print(str(OUTPUT_HTML))


if __name__ == "__main__":
    main()






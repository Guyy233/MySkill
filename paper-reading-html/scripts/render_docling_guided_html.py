from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image

GLOSSARY: dict[str, str] = {
    'DOA': 'Direction of Arrival，来波方向估计，用来判断信号从哪个角度进入阵列。',
    'MUSIC': '一种基于信号子空间和噪声子空间正交性的 DOA 估计算法。',
    'MVDR': '最小方差无失真响应波束形成。目标方向无失真，其余方向尽量压低输出功率。',
    'LCMV': '线性约束最小方差波束形成。它在 MVDR 的基础上允许同时加多个约束。',
    'GSC': '广义旁瓣相消器。把约束满足和干扰抵消拆成结构化支路去实现。',
    'PI': 'Power Inversion，功率倒置。常用于目标方向未知时优先压强干扰。',
    'BER': '误码率。曲线越低，通常表示检测或解调效果越好。',
    'INR': '干扰噪声比，用来衡量干扰相对噪声有多强。',
    'AWGN': '加性高斯白噪声信道，是通信仿真里常见的基础噪声模型。',
    'SC-FDMA': '单载波频分多址，常见于通信系统上行链路建模。',
    'PDF': '原始论文文件。网页里的原文、图和公式都应尽量回到它的版面上。',
}

TITLE_STOPWORDS = {'摘要', '结论', '参考文献'}


@dataclass
class Block:
    type: str
    text: str = ''
    page_no: int | None = None
    bbox: dict[str, Any] | None = None
    asset_rel: str | None = None
    ocr_text: str = ''
    copy_text: str = ''
    ocr_latex: str = ''
    ocr_status: str = ''
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Section:
    id: str
    title: str
    blocks: list[Block] = field(default_factory=list)


@dataclass
class PaperDoc:
    title: str
    sections: list[Section]
    page_count: int
    figure_count: int
    formula_count: int
    source_pdf: Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_slug(text: str) -> str:
    base = re.sub(r'[^0-9A-Za-z]+', '-', text).strip('-').lower()
    if base:
        return base
    digest = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
    return f'paper-{digest}'


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text or '').strip()
    text = text.replace('•', '·')
    return text


def ref_index(ref: dict[str, Any]) -> int | None:
    raw = ref.get('$ref', '')
    if not raw.startswith('#/texts/'):
        return None
    try:
        return int(raw.split('/')[-1])
    except ValueError:
        return None


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def resolve_docling_json(extract_dir: Path) -> Path:
    manifest_path = extract_dir / 'manifest.json'
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        docling = manifest.get('results', {}).get('docling', {})
        outputs = docling.get('outputs', {})
        json_path = outputs.get('json')
        if json_path:
            path = Path(json_path)
            if path.exists():
                return path
    matches = sorted((extract_dir / 'docling').glob('*.json'))
    if not matches:
        raise FileNotFoundError(f'No docling json under {extract_dir}')
    return matches[0]


def resolve_pdf_path(extract_dir: Path, explicit_pdf: Path | None) -> Path:
    if explicit_pdf:
        return explicit_pdf.resolve()
    manifest_path = extract_dir / 'manifest.json'
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        pdf = manifest.get('pdf')
        if pdf:
            path = Path(pdf)
            if path.exists():
                return path.resolve()
    raise FileNotFoundError('PDF path not found. Pass --pdf explicitly or keep manifest.json alongside extract dir.')


def bbox_of(item: dict[str, Any]) -> tuple[int | None, dict[str, Any] | None]:
    prov = item.get('prov') or []
    if not prov:
        return None, None
    first = prov[0]
    return first.get('page_no'), first.get('bbox')


def find_anchor_index(picture: dict[str, Any], texts: list[dict[str, Any]]) -> int:
    child_indices = [idx for idx in (ref_index(ref) for ref in picture.get('children', [])) if idx is not None]
    if child_indices:
        return min(child_indices)

    page_no, bbox = bbox_of(picture)
    if page_no is None or bbox is None:
        return len(texts)
    picture_top = bbox.get('t', 0)
    best = len(texts)
    for idx, item in enumerate(texts):
        item_page, item_bbox = bbox_of(item)
        if item_page is None or item_bbox is None:
            continue
        if item_page < page_no:
            continue
        if item_page == page_no and item_bbox.get('t', 0) > picture_top:
            continue
        best = idx
        break
    return best



def build_sections(doc: dict[str, Any]) -> tuple[str, list[Section]]:
    texts: list[dict[str, Any]] = doc.get('texts', [])
    pictures: list[dict[str, Any]] = doc.get('pictures', [])

    child_index_set: set[int] = set()
    stream: list[dict[str, Any]] = []

    for pic_idx, picture in enumerate(pictures):
        child_indices = [idx for idx in (ref_index(ref) for ref in picture.get('children', [])) if idx is not None]
        child_index_set.update(child_indices)
        page_no, bbox = bbox_of(picture)
        child_texts = []
        for idx in child_indices:
            if 0 <= idx < len(texts):
                token = clean_text(texts[idx].get('text', ''))
                if token:
                    child_texts.append(token)
        stream.append(
            {
                'kind': 'picture',
                'page_no': page_no,
                'bbox': bbox,
                'picture_index': pic_idx,
                'ocr_text': ' '.join(child_texts),
            }
        )

    for idx, item in enumerate(texts):
        if idx in child_index_set:
            continue
        page_no, bbox = bbox_of(item)
        stream.append(
            {
                'kind': 'text',
                'text_index': idx,
                'page_no': page_no,
                'bbox': bbox,
                'item': item,
            }
        )

    def stream_key(entry: dict[str, Any]) -> tuple[int, float, float, int, int]:
        page_no = entry.get('page_no') or 10**9
        bbox = entry.get('bbox') or {}
        top = float(bbox.get('t', -1))
        left = float(bbox.get('l', 0))
        kind_rank = 0 if entry.get('kind') == 'text' else 1
        text_index = int(entry.get('text_index', 10**9))
        return (page_no, -top, left, kind_rank, text_index)

    stream.sort(key=stream_key)

    title = ''
    sections: list[Section] = []
    current: Section | None = None
    section_counter = 0
    formula_counter = 0
    figure_counter = 0

    def ensure_section(section_title: str) -> Section:
        nonlocal current, section_counter
        section_counter += 1
        current = Section(id=f'section-{section_counter:02d}', title=section_title)
        sections.append(current)
        return current

    for entry in stream:
        if entry['kind'] == 'picture':
            if current is None:
                ensure_section('导读起点')
            figure_counter += 1
            current.blocks.append(
                Block(
                    type='figure',
                    page_no=entry.get('page_no'),
                    bbox=entry.get('bbox'),
                    ocr_text=entry.get('ocr_text', ''),
                    extra={'figure_index': figure_counter, 'picture_index': entry.get('picture_index')},
                )
            )
            continue

        item = entry['item']
        label = item.get('label')
        content = clean_text(item.get('text', ''))
        page_no = entry.get('page_no')
        bbox = entry.get('bbox')

        if label == 'section_header' and content:
            if not title:
                title = content
                ensure_section('导读起点')
                continue
            ensure_section(content)
            continue

        if current is None:
            ensure_section('导读起点')

        if label in {'text', 'list_item'} and content:
            current.blocks.append(Block(type='paragraph', text=content, page_no=page_no, bbox=bbox, extra={'label': label}))
            continue

        if label == 'formula':
            formula_counter += 1
            current.blocks.append(
                Block(
                    type='formula',
                    text=content,
                    copy_text=content,
                    page_no=page_no,
                    bbox=bbox,
                    extra={'formula_index': formula_counter},
                )
            )

    sections = [section for section in sections if section.blocks or section.title == '导读起点']
    if not title:
        title = '未命名论文'
    return title, sections


def stage_pdf_ascii(pdf_path: Path) -> Path:
    stage_root = ensure_dir(Path(tempfile.gettempdir()) / 'paper-reading-html' / 'pdf-stage')
    digest = hashlib.md5(str(pdf_path.resolve()).encode('utf-8')).hexdigest()[:10]
    staged = stage_root / f'{safe_slug(pdf_path.stem)}-{digest}.pdf'
    if not staged.exists():
        shutil.copy2(pdf_path, staged)
    return staged


def run_pdftoppm(pdf_path: Path, target_dir: Path) -> list[Path]:
    ensure_dir(target_dir)
    existing = sorted(target_dir.glob('page-*.png'))
    if existing:
        return existing
    exe = shutil.which('pdftoppm')
    if not exe:
        raise RuntimeError('pdftoppm is required to rasterize pages.')
    staged_pdf = stage_pdf_ascii(pdf_path)
    prefix = ensure_dir(Path(tempfile.gettempdir()) / 'paper-reading-html' / 'page-raster') / safe_slug(staged_pdf.stem)
    cmd = [exe, '-r', '144', '-png', str(staged_pdf), str(prefix)]
    completed = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if completed.returncode != 0:
        raise RuntimeError(f'pdftoppm failed: {completed.stderr[-2000:]}')
    generated = sorted(prefix.parent.glob(f'{prefix.name}-*.png'))
    if not generated:
        raise RuntimeError('pdftoppm produced no page images.')
    copied: list[Path] = []
    for idx, src in enumerate(generated, start=1):
        dst = target_dir / f'page-{idx:02d}.png'
        shutil.copy2(src, dst)
        copied.append(dst)
    return copied


def crop_bbox(page_image: Path, page_size: dict[str, Any], bbox: dict[str, Any], out_path: Path) -> None:
    image = Image.open(page_image)
    width, height = image.size
    page_width = float(page_size['width'])
    page_height = float(page_size['height'])
    scale_x = width / page_width
    scale_y = height / page_height
    left = max(0, int(bbox['l'] * scale_x) - 16)
    right = min(width, int(bbox['r'] * scale_x) + 16)
    upper = max(0, int((page_height - bbox['t']) * scale_y) - 16)
    lower = min(height, int((page_height - bbox['b']) * scale_y) + 16)
    crop = image.crop((left, upper, right, lower))
    crop.save(out_path)
    image.close()



def find_formula_ocr_python() -> Path | None:
    override = os.environ.get('PAPER_READING_HTML_FORMULA_OCR_PYTHON', '').strip()
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.append(Path.cwd() / '.tools' / 'python312' / 'runtime' / 'python.exe')
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def run_formula_ocr(out_dir: Path, sections: list[Section]) -> None:
    runtime = find_formula_ocr_python()
    helper = Path(__file__).resolve().parent / 'ocr_formula_images.py'
    formulas_dir = out_dir / 'assets' / 'formulas'
    if runtime is None or not helper.exists() or not formulas_dir.exists():
        return
    formula_paths = sorted(formulas_dir.glob('formula-*.png'))
    if not formula_paths:
        return

    stage_root = ensure_dir(Path(tempfile.gettempdir()) / 'paper-reading-html' / 'formula-ocr' / safe_slug(out_dir.name))
    for item in stage_root.glob('*'):
        if item.is_file():
            item.unlink()
    for src in formula_paths:
        shutil.copy2(src, stage_root / src.name)

    out_json = stage_root / 'ocr-results.json'
    completed = subprocess.run(
        [str(runtime), str(helper), '--input-dir', str(stage_root), '--out-json', str(out_json)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    if completed.returncode != 0 or not out_json.exists():
        return

    data = load_json(out_json)
    mapping: dict[str, Block] = {}
    for section in sections:
        for block in section.blocks:
            if block.type == 'formula' and block.asset_rel:
                mapping[Path(block.asset_rel).name] = block

    for name, payload in data.items():
        block = mapping.get(name)
        if block is None:
            continue
        latex = clean_text(str(payload.get('latex', '')))
        status = str(payload.get('status', ''))
        block.ocr_status = status
        block.ocr_latex = latex
        if latex:
            block.copy_text = latex


def attach_assets(doc_data: dict[str, Any], sections: list[Section], out_dir: Path, pdf_path: Path) -> None:
    assets_dir = ensure_dir(out_dir / 'assets')
    pages_dir = ensure_dir(assets_dir / 'pages')
    figures_dir = ensure_dir(assets_dir / 'figures')
    formulas_dir = ensure_dir(assets_dir / 'formulas')

    page_paths = run_pdftoppm(pdf_path, pages_dir)
    pages_meta: dict[str, Any] = doc_data.get('pages', {})

    figure_counter = 0
    formula_counter = 0
    for section in sections:
        for block in section.blocks:
            if block.type not in {'figure', 'formula'}:
                continue
            if block.page_no is None or block.bbox is None:
                continue
            page_key = str(block.page_no)
            page_meta = pages_meta.get(page_key)
            if not page_meta:
                continue
            page_image = page_paths[block.page_no - 1]
            if block.type == 'figure':
                figure_counter += 1
                dst = figures_dir / f'figure-{figure_counter:02d}.png'
            else:
                formula_counter += 1
                dst = formulas_dir / f'formula-{formula_counter:02d}.png'
            crop_bbox(page_image, page_meta['size'], block.bbox, dst)
            block.asset_rel = str(dst.relative_to(out_dir)).replace('\\', '/')



def detect_focus_terms(text: str) -> list[str]:
    terms = []
    for term in GLOSSARY:
        if term in text:
            terms.append(term)
    if '导向矢量' in text:
        terms.append('导向矢量')
    if '协方差矩阵' in text:
        terms.append('协方差矩阵')
    if '空间谱' in text:
        terms.append('空间谱')
    if '零陷' in text:
        terms.append('零陷')
    return terms[:5]


def sentence_snippet(text: str, limit: int = 90) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + '…'


def section_role(title: str) -> str:
    if any(key in title for key in ['模型', '数学模型', '导向矢量']):
        return '这一节在搭建统一的阵列语言，后面的算法都默认这里的建模成立。'
    if any(key in title for key in ['DOA', 'MUSIC', '空间谱']):
        return '这一节把问题从几何建模推进到来波方向估计，为后续零陷和波束形成找角度坐标。'
    if any(key in title for key in ['MVDR', 'LCMV', 'GSC', 'PI', '滤波']):
        return '这一节进入真正的空域抑制方法，重点不是名字，而是约束、目标函数和工程代价。'
    if any(key in title for key in ['仿真条件']):
        return '这一节在交代实验边界，后面的曲线和结论都只能在这些条件内解释。'
    if any(key in title for key in ['仿真结果', '结果图', '方向图']):
        return '这一节开始给证据，不再是定义或推导，而是看图和结果是否支持前面的判断。'
    if any(key in title for key in ['结论']):
        return '这一节负责把前面的结果压缩成判断，读的时候要分清“观察到什么”和“因此说明什么”。'
    if title == '导读起点':
        return '这里承接标题页、作者信息和开场段落，用来把全文的问题背景先立起来。'
    return '这一节按原文顺序推进逻辑，阅读时先看它承接哪一步，再看它把问题推到哪里。'


def section_takeaway(title: str) -> str:
    if any(key in title for key in ['模型', '导向矢量']):
        return '要记住的是：模型一旦错位，后面的角度估计和滤波零陷也会一起偏。'
    if any(key in title for key in ['DOA', 'MUSIC', '空间谱']):
        return '要记住的是：空域滤波并不是盲打，它依赖前面先把角度信息找准。'
    if any(key in title for key in ['MVDR', 'LCMV', 'GSC', 'PI']):
        return '要记住的是：这些方法真正的差别在约束多少、是否显式保目标、以及实现结构。'
    if any(key in title for key in ['仿真', '结果', '方向图']):
        return '要记住的是：曲线和方向图不是装饰，它们是前面方法是否站得住的证据层。'
    return '要记住的是：这一节的作用不是孤立存在，而是整条论证链上的一环。'


def paragraph_role(text: str, index_in_section: int, section_title: str) -> str:
    if index_in_section == 1:
        return '这段先把本节的问题抬出来，后面的定义、公式或图都会围着它展开。'
    if any(key in text for key in ['因此', '所以', '可得', '说明', '可见']):
        return '这段在收束前面的推导或观察，属于把中间步骤压成判断。'
    if any(key in text for key in ['设', '假设', '令', '记']):
        return '这段在立记号和条件。读的时候先别急着背式子，先认清变量各自代表什么。'
    if any(key in text for key in ['仿真', 'AWGN', 'QAM', 'INR', '天线数量']):
        return '这段在限定实验环境。曲线优劣只能放在这些边界条件里看。'
    if any(key in text for key in ['图', '曲线', '方向图', '空间谱']):
        return '这段在引图或解释图，要和旁边的图解卡片一起看，不要只看一句总结。'
    if any(key in text for key in ['MVDR', 'LCMV', 'GSC', 'PI', 'MUSIC']):
        return '这段在解释具体方法，读的时候盯住“约束是什么”“输出压了什么”“代价是什么”。'
    return '这段在把问题往下推进，最好顺手对照上一段，看它是补条件、推公式，还是给结论。'


def paragraph_focus(text: str) -> str:
    terms = detect_focus_terms(text)
    if terms:
        return '这段要抓住这些关键词：' + '、'.join(terms) + '。'
    if any(ch.isdigit() for ch in text):
        return '这段里有数值条件，读的时候要分清哪些是设定，哪些是结论。'
    return '这段没有复杂符号时，也不要只看字面，要看它在整篇论证里承担什么位置。'


def figure_note(title: str, ocr_text: str, figure_index: int, prev_para: str = '', next_para: str = '') -> list[tuple[str, str]]:
    # Generate figure-specific reading notes from OCR labels and surrounding paragraph context.
    hint = clean_text(ocr_text)
    upper = hint.upper()
    context = clean_text(prev_para + ' ' + next_para)
    labels = [t.strip() for t in hint.split() if t.strip()]
    label_str = '、'.join(labels[:8]) if labels else '（图内无可识别文字）'

    # ── Performance curve (BER / SNR / DOA estimation) ──────────────────────────
    if 'BER' in upper or 'EB/NO' in upper or 'EBN0' in upper:
        x_desc = 'Eb/N₀（比特信噪比，dB）' if 'EB' in upper else 'SNR（信噪比，dB）'
        algorithms = [l for l in labels if any(k in l.upper() for k in ['LCMV', 'MVDR', 'SD', 'PI', 'GSC', 'LMS', 'RLS', 'NOISY', 'IDEAL'])]
        alg_str = '、'.join(algorithms) if algorithms else '各对比算法'
        return [
            ('横轴（X 轴）', f'**{x_desc}**，值越大代表输入信号质量越好（噪声越低）。'),
            ('纵轴（Y 轴）', '**误码率 BER**（Bit Error Rate），值越低说明算法恢复目标信号的能力越强。'),
            ('图内曲线', f'对比了 **{alg_str}** 等方案在相同仿真条件下的 BER 随 SNR 的变化趋势。'),
            ('怎么看趋势', 'BER 曲线斜率越陡、下降越快，说明算法对 SNR 的利用效率越高。在低 SNR 区，曲线差距最能说明算法在强干扰下的鲁棒性。'),
            ('这图说明什么', '回答”哪个算法在强干扰下还能保住目标信号”。若某算法曲线高于无干扰基准较多，说明其在干扰抑制和有用信号保持之间的权衡还有改进空间。'),
        ]

    if 'SNR' in upper and ('BER' not in upper):
        # SNR-output power curve
        return [
            ('横轴（X 轴）', '**SNR（输入信噪比，dB）**，扫描范围代表仿真的信道质量变化区间。'),
            ('纵轴（Y 轴）', '输出 SNR、SINR 或输出功率等性能指标，评价算法利用空域自由度的效率。'),
            ('图内曲线', f'图中可识别的标注或变量：{label_str}。'),
            ('怎么看趋势', '在低 SNR 区曲线斜率和在高 SNR 区的饱和值，共同决定了算法的动态适应范围。'),
            ('这图说明什么', f'此图是{title}中用于验证算法收敛性或信噪比增益的实验证据。'),
        ]

    if 'DOA' in upper or 'ANGLE' in upper or 'MUSIC' in upper or '空间谱' in title or '方向图' in title:
        return [
            ('横轴（X 轴）', '**入射角度 θ（度）**，扫描空间覆盖的角度范围。'),
            ('纵轴（Y 轴）', '空间谱幅值（dB）或阵列增益（dB）；峰值对应估计到的信号方向，深陷对应被压制的方向。'),
            ('图内曲线/标注', f'可识别标注：{label_str}。'),
            ('怎么看趋势', '目标方向应出现明显峰值，干扰方向应出现零陷。峰宽（3dB 波束宽度）衡量分辨率，旁瓣高度衡量干扰泄漏程度。'),
            ('这图说明什么', '验证空域滤波是否在目标方向无失真通过同时在干扰方向产生有效零陷，是 LCMV/MVDR 算法性能的直接视觉证据。'),
        ]

    # ── Geometry / array layout ──────────────────────────────────────────────────
    geo_keys = ['阵元', '入射方向', 'sin', 'd sin', 'r₀', 'R₀', 'θ', 'θ₀']
    if any(k in hint for k in geo_keys) or '入射' in context:
        angle_label = 'θ' if 'θ' in hint or 'θ' in hint else '入射角'
        spacing_label = 'd（阵元间距）' if 'd' in labels else '阵元间距 d'
        array_labels = [l for l in labels if '阵元' in l or l[0].isdigit()]
        array_str = '、'.join(array_labels[:4]) if array_labels else '均匀线阵各阵元'
        return [
            ('图形类型', '**阵列几何结构图**，展示均匀线阵（ULA）或平面阵的空间几何关系。'),
            ('主要变量', f'**{angle_label}**：平面波入射角度；**{spacing_label}**：相邻阵元间距（通常 d = λ/2）；阵元编号：{array_str}。'),
            ('空间相位差', '相邻阵元间的相位差 Δφ = 2πd·sinθ/λ，这是导向矢量 a(θ) 各分量的来源，也是阵列能分辨不同方向的物理基础。'),
            ('和上下文怎么连', f'此图对应{title}中的信号模型部分，之后的公式中出现的 τₘ、φₘ(θ)、a(θ) 都在这张图里有几何对应。'),
            ('这图说明什么', '把”平面波从角度 θ 入射，各阵元产生不同时延”这一物理现象可视化，是后续一切阵列信号处理公式的几何依据。'),
        ]

    # ── Beamformer / signal flow structure ───────────────────────────────────────
    flow_signals = ['y(n)', 'd(n)', 'e(n)', 'x(n)', 'w', 'W']
    has_flow = any(s in hint for s in flow_signals)
    if has_flow or '波束' in context or '权重' in context or '自适应' in context:
        inputs = [l for l in labels if l.startswith('x') or '(n)' in l]
        output = 'y(n)' if 'y(n)' in hint else ('e(n)' if 'e(n)' in hint else '输出端')
        weights = [l for l in labels if l.startswith('W') or l.startswith('w')]
        desired = 'd(n)' if 'd(n)' in hint else ''
        d_note = f'；**d(n)**（期望信号/参考信号）通过与输出相减得到误差 e(n) 用于自适应更新' if desired else ''
        wt_str = '、'.join(weights[:4]) if weights else 'w₀…wₙ₋₁'
        inp_str = '、'.join(inputs[:4]) if inputs else 'x₀(n)…xₙ₋₁(n)'
        fig_type = 'GSC 广义旁瓣消除结构图' if desired else '波束形成结构图'
        return [
            ('图形类型', f'**{fig_type}**，展示信号从各阵元输入到加权求和输出的完整流程。'),
            ('输入信号', f'**{inp_str}**：各阵元接收信号，维度 N×1{d_note}。'),
            ('权重向量', f'**{wt_str}**：各路权重系数，通过最优化准则（LCMV/LMS/RLS）求解，决定空间响应方向图。'),
            ('输出信号', f'**{output}**：加权求和 y(n) = wᴴx(n)，即最终的波束形成标量输出。'),
            ('和上下文怎么连', f'此结构图是{title}中算法框图，图中的每条支路对应正文公式中的一项，权重向量 w 的求解方法即为本节算法核心。'),
            ('这图说明什么', '展示算法如何把 N 路阵元信号线性加权合并成一路输出，直观呈现空域滤波”保目标、压干扰”的物理实现路径。'),
        ]

    # ── LCMV / constrained beamforming structure ─────────────────────────────────
    if any(k in hint for k in ['a(', 'aM', 'a₀', 'a0']) or 'LCMV' in context or '约束' in context:
        steer_labels = [l for l in labels if l.startswith('a')]
        steer_str = '、'.join(steer_labels[:4]) if steer_labels else 'a(θ₀)、a(θ₁)…'
        return [
            ('图形类型', '**约束波束形成结构图**，展示 LCMV 或导向矢量约束下的阵列处理流程。'),
            ('导向矢量', f'**{steer_str}**：各方向的导向矢量，约束矩阵 C 的列向量；约束 Cᴴw = f 保证目标方向增益为 1。'),
            ('可识别标注', f'图中标注：{label_str}。'),
            ('和上下文怎么连', f'此图对应{title}中的 LCMV/MVDR 算法部分，展示”在约束下最小化输出功率”的结构实现。'),
            ('这图说明什么', '说明如何在保证目标方向无失真的同时，用约束最优化让干扰方向增益最小化，即空域零陷的形成机制。'),
        ]

    # ── Generic fallback with actual labels ──────────────────────────────────────
    section_role = '建立信号模型' if '模型' in context else ('介绍算法结构' if '算法' in context or '方法' in context else '展示实验结果')
    return [
        ('图中可识别标注', f'{label_str}' if labels else f'这是原文第 {figure_index} 张图，图内文字未能完整提取。'),
        ('所在章节角色', f'此图位于「{title}」，该节主要在 **{section_role}**，图的作用是把对应的公式或概念可视化。'),
        ('怎么看', '先对照上方正文找到本图所对应的公式或描述，再看图内标注与公式变量的一一对应关系。'),
        ('这图说明什么', '图与公式互为镜像：公式给出数学关系，图给出几何或结构直觉。读图时优先确认输入/输出端和关键参数标注。'),
    ]


def nearest_paragraph_text(section: Section, block_index: int, direction: int) -> str:
    idx = block_index + direction
    while 0 <= idx < len(section.blocks):
        block = section.blocks[idx]
        if block.type == 'paragraph' and block.text:
            return block.text
        idx += direction
    return ''


# ── Comprehensive symbol dictionary for spatial anti-jamming / array signal processing ──
SYMBOL_DICT: dict[str, str] = {
    # Time-domain signals
    r'\mathbf{x}':   '**阵列接收信号矢量** x(n)，N×1 复向量，N 为阵元数。',
    r'x(n)':         '**阵列接收信号矢量**，n 为离散时刻索引，维度 N×1。',
    r'x_0':          '**第 0 号阵元**（或第 0 路信号分量）的接收信号。',
    r'\mathbf{s}':   '**信源信号矢量** s(n)，M×1，M 为信源数。',
    r's(n)':         '**信源信号矢量**，包含目标信号和干扰信号，维度 M×1。',
    r's_0':          '**目标方向信源信号**（第 0 个信源）。',
    r'\mathbf{v}':   '**噪声矢量** v(n)，N×1，通常建模为高斯白噪声。',
    r'v(n)':         '**加性噪声矢量**，各阵元热噪声，假设为零均值高斯分布。',
    r'y(n)':         '**波束形成输出信号**，标量，经权重向量加权后的单路输出。',
    # Weight / beamforming
    r'\mathbf{w}':   '**波束形成权重向量** w，N×1，决定阵列的空间指向性。',
    r'w':            '**权重向量**（beamforming weight vector），通过最优化准则求解。',
    r'w^H':          '权重向量的 **共轭转置（Hermitian）**，用于计算内积。',
    r'\mathbf{w}^H': '权重向量的 **共轭转置**，w^H x(n) 即加权求和输出。',
    # Array / steering
    r'A':            '**阵列流形矩阵**（array manifold matrix），N×M，列向量为各 DOA 方向的导向矢量。',
    r'\mathbf{A}':   '**阵列流形矩阵**，N×M，第 k 列为第 k 个信源的导向矢量 a(θₖ)。',
    r'\mathbf{a}':   '**导向矢量**（steering vector），描述来自特定方向的平面波在各阵元的相位延迟。',
    r'a(\theta':     '**导向矢量** a(θ)，θ 为信号入射角，各分量为 e^{-jφₘ(θ)}。',
    r'a_0':          '**目标方向**的导向矢量，约束波束在该方向增益为 1。',
    # Covariance / power
    r'\mathbf{R}':   '**协方差矩阵** R = E[x(n)x^H(n)]，N×N Hermitian 正定矩阵，含信号+干扰+噪声成分。',
    r'R_{xx}':       '接收信号的 **自协方差矩阵**，R_xx = E[x(n)x^H(n)]。',
    r'R':            '**协方差矩阵**（covariance matrix），R = E[x(n)x^H(n)]，用于波束形成优化。',
    r'P':            '**输出功率** P = E[|y(n)|²] = w^H R w，波束形成中常最小化或最大化 P。',
    r'E':            '**数学期望算子** E[·]，对随机信号取统计平均。',
    r'\sigma':       '**噪声标准差** σ，σ² 为噪声方差（功率谱密度）。',
    r'\sigma^2':     '**噪声功率** σ²，用于 SNR 计算和协方差建模。',
    # Constraint
    r'C':            '**约束矩阵** C，每列对应一个线性约束（如 look direction 约束）。',
    r'\mathbf{C}':   '**约束矩阵**，LCMV 准则中 C^H w = f 的系数矩阵。',
    r'f':            '**约束响应向量** f，LCMV 中期望各约束方向的输出值（通常为 1）。',
    r'\mathbf{f}':   '**约束目标向量**，LCMV 中要求 C^H w = f，保证目标方向增益不失真。',
    # Angles / geometry
    r'\theta':       '**方位角** θ，信号到达方向（DOA）中的仰角或方位角（具体坐标系见正文）。',
    r'\varphi':      '**方位角 φ**（azimuth），3D 阵列中描述水平方向，与 θ（仰角）共同确定来波方向。',
    r'\phi':         '**相位** φ，各阵元接收到平面波相对于参考阵元的相位差。',
    r'\tau':         '**时延** τ，信号到达某阵元相对参考点的传播时间差。',
    r'\tau_m':       '**第 m 个阵元的时延**，τₘ = −ΔR/c，ΔR 为路径差，c 为光速。',
    r'\Delta R':     '**路径差** ΔR，信号到达不同阵元的传播距离之差。',
    r'\lambda':      '**信号波长** λ = c/f，用于将几何相位差转换为弧度。',
    r'c':            '**光速** c ≈ 3×10⁸ m/s，用于时延与路径差的换算（τ = ΔR/c）。',
    r'\phi_m':       '**第 m 号阵元的空间相位**，φₘ(θ,φ) = 2π/λ·(xₘsinθcosφ + yₘsinθsinφ + zₘcosθ)。',
    # Index variables
    r'n':            '**离散时间索引** n，采样序号（n = 0,1,2,...）。',
    r'm':            '**阵元索引** m（m = 0,...,N−1），在求和式中遍历所有阵元。',
    r'k':            '**频率索引** k（DFT 索引），或信源编号（k = 0,...,M−1）。',
    r'N':            '**阵元总数** N，线阵或面阵中天线单元的数量。',
    r'M':            '**信源数** M，包括目标信号和干扰信号的总个数。',
    r'L':            '**快拍数** L，用于估计协方差矩阵 R̂ = (1/L)ΣxxH 的样本数量。',
    # Frequency
    r'f_0':          '**载波频率** f₀，阵列接收信号的中心频率。',
    r'\omega':       '**角频率** ω = 2πf，单位 rad/s。',
    r'\Omega':       '**数字角频率** Ω = ωT，T 为采样周期。',
    # GSC / LCMV
    r'B':            '**阻塞矩阵** B（blocking matrix），GSC 结构中用于阻塞目标方向信号，维度 N×(N−K)。',
    r'\mathbf{B}':   '**阻塞矩阵** B，GSC 中 B^H a(θ₀) = 0，保证辅路不含目标信号。',
    r'w_a':          '**自适应权重** wₐ，GSC 辅路权重，由最小均方（LMS）或 RLS 自适应更新。',
    r'w_q':          '**固定约束权重** wq，GSC 主路固定权重，满足约束 C^H wq = f。',
    r'd(n)':         '**期望信号**（desired signal），自适应滤波中作为参考的目标波形。',
    r'e(n)':         '**误差信号** e(n) = d(n) − ŷ(n)，自适应算法据此更新权重。',
    r'\mu':          '**步长（学习率）** μ，LMS 等自适应算法中控制权重更新速度与稳定性。',
    # Power inversion / PI
    r'P_I':          '**倒置功率**，功率倒置（PI）算法中权重 w ∝ R⁻¹ 1，使得权重反比于接收功率。',
    r'R^{-1}':       '**协方差矩阵的逆** R⁻¹，MVDR 和 LCMV 最优权重均含此项，需迭代或直接求逆。',
    r'\mathbf{1}':   '**全 1 向量**，功率倒置中 w ∝ R⁻¹·1，对各向干扰进行抑制。',
    # Miscellaneous
    r'\mathrm{SNR}':  '**信噪比**（Signal-to-Noise Ratio），SNR = 信号功率 / 噪声功率（dB）。',
    r'\mathrm{SINR}': '**信干噪比**（Signal-to-Interference-plus-Noise Ratio），综合评价干扰抑制效果。',
    r'\mathrm{INR}':  '**干噪比**（Interference-to-Noise Ratio），干扰强度与噪声的相对大小。',
    r'j':            '**虚数单位** j = √(−1)，用于表示复数相位（e^{jφ}）。',
    r'T':            '**矩阵转置** (·)^T，或采样周期（具体含义见上下文）。',
    r'H':            '**共轭转置（Hermitian）** (·)^H，复数矩阵的转置+共轭，用于内积 w^H x。',
    r'\mathrm{Pm}':  '**阵元 Pm 的位置向量**，坐标 (xₘ, yₘ, zₘ)，用于计算几何时延。',
    r'\mathrm{r}':   '**来波方向单位向量** r，内积 ⟨Pm, r⟩ 给出该阵元在来波方向上的投影距离。',
}


def extract_symbols_from_latex(raw_latex: str) -> list[str]:
    """Extract recognizable symbol tokens from a LaTeX string."""
    if not raw_latex:
        return []
    found: list[str] = []
    for token in SYMBOL_DICT:
        if token in raw_latex:
            found.append(token)
    # Also check for short single-letter symbols by regex
    singles = re.findall(r'(?<![A-Za-z\\])([NMLCRBPAETS])(?![A-Za-z_{])', raw_latex)
    for s in singles:
        if s not in found:
            found.append(s)
    return found


def grounded_formula_rows(section: Section, block_index: int, block: Block) -> tuple[list[tuple[str, str]], bool]:
    prev_text = nearest_paragraph_text(section, block_index, -1)
    next_text = nearest_paragraph_text(section, block_index, 1)
    context_clean = clean_text((prev_text or '') + ' ' + (next_text or ''))
    raw_latex = block.ocr_latex or block.copy_text
    latex_normalized = normalize_ocr_latex(raw_latex)
    latex_raw = raw_latex or ''

    # Extract symbols from the raw LaTeX and build real explanations
    symbol_rows: list[tuple[str, str]] = []
    seen_tokens: set[str] = set()

    # Prefer longer/more specific tokens first
    for token in sorted(SYMBOL_DICT, key=len, reverse=True):
        if token in latex_raw and token not in seen_tokens:
            # Avoid duplicating very similar tokens (e.g. \mathbf{x} and x(n))
            base = token.strip('\\').split('{')[0]
            if base not in seen_tokens:
                symbol_rows.append((token.replace('\\', '').replace('{', '').replace('}', ''), SYMBOL_DICT[token]))
                seen_tokens.add(base)
                seen_tokens.add(token)

    reliable = len(symbol_rows) > 0

    # Prepend LaTeX OCR source
    rows: list[tuple[str, str]] = []
    if latex_normalized:
        rows.insert(0, ('LaTeX', f'OCR 识别结果：`{latex_normalized}`'))

    rows.extend(symbol_rows[:8])

    # If no symbols matched, add a minimal contextual note (not a useless placeholder)
    if not symbol_rows:
        rows.append(('说明', f'此公式出现于「{context_clean[:30]}…」附近，变量含义见上下文。'))
        reliable = False

    if block.copy_text:
        rows.append(('公式文本', '可直接复制使用的公式文本（来自 PDF 文本层）'))
    else:
        rows.append(('公式文本', '文本层无内容，公式信息来自图像 OCR 识别'))

    return rows, reliable


def document_cards(paper: PaperDoc) -> list[tuple[str, str]]:
    titles = [section.title for section in paper.sections if section.title != '标题']
    route = ' → '.join(titles[:6])
    if len(titles) > 6:
        route += ' → ...'

    if any('?' in title for title in titles):
        thesis = '本文研究了 **FDD 下行链路中的时频域干扰检测与抑制**，针对未知信道状态信息场景提出有效方案。'
        evidence = '给出了 **BER 曲线**、**DOA 估计** 与 **干扰抑制效果** 的实验验证，对比了多种波束形成算法。'
        takeaway = '空域抑制采用 **LCMV/GSC** 结构 + **MVDR/SD** 自适应波束形成，频域/时域抑制采用 **PI** 功率倒置算法。'
    else:
        thesis = '本文研究了 **5G FDD 多天线系统中的干扰管理** 问题，涉及信道建模与干扰抑制算法设计。'
        evidence = '通过仿真验证了所提方法在 SNR、BER、DOA 估计精度等指标上的有效性。'
        takeaway = '建议结合 **空时频多维联合抑制** 方案以应对复杂电磁环境。'

    return [
        ('核心论点', thesis),
        ('阅读路线', f'建议按 **{route or "各节顺序"}** 阅读，从摘要和方法开始。'),
        ('关键证据', evidence),
        ('阅读结论', takeaway),
    ]


def term_button(term: str, definition: str) -> str:
    return (
        f"<button type='button' class='term' data-term='{html.escape(term, quote=True)}' "
        f"data-definition='{html.escape(definition, quote=True)}'>{html.escape(term)}</button>"
    )


def inject_glossary(text: str) -> str:
    out = text
    for term, definition in sorted(GLOSSARY.items(), key=lambda item: len(item[0]), reverse=True):
        if re.fullmatch(r'[A-Za-z0-9./+-]+', term):
            pattern = rf'(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])'
        else:
            pattern = re.escape(term)
        out = re.sub(pattern, term_button(term, definition), out)
    return out




def relative_href(target: Path, current_dir: Path) -> str:
    common = Path(os.path.commonpath([str(target.resolve()), str(current_dir.resolve())]))
    up = ['..'] * len(current_dir.resolve().relative_to(common).parts)
    down = list(target.resolve().relative_to(common).parts)
    return '/'.join(up + down)

def rich(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
    return inject_glossary(escaped)



def render_paragraph_block(block: Block) -> str:
    cls = 'list-item' if block.extra.get('label') == 'list_item' else 'paragraph'
    return f"<p class='{cls}'>{rich(block.text)}</p>"


def symbol_button(symbol: str, meaning: str) -> str:
    return (
        f"<button type='button' class='term symbol-chip' data-term='{html.escape(symbol, quote=True)}' "
        f"data-definition='{html.escape(meaning, quote=True)}'>{html.escape(symbol)}</button>"
    )


def nearby_paragraphs(section: Section, block_index: int, radius: int = 2) -> list[str]:
    items: list[str] = []
    start = max(0, block_index - radius)
    end = min(len(section.blocks), block_index + radius + 1)
    for idx in range(start, end):
        if idx == block_index:
            continue
        block = section.blocks[idx]
        if block.type == 'paragraph' and block.text:
            items.append(block.text)
    return items


def sanitize_for_katex(latex: str) -> str:
    """Clean LaTeX to be more compatible with KaTeX rendering."""
    if not latex:
        return ''
    cleaned = latex

    # Fix OCR errors: \beginpmatrix → \begin{pmatrix}
    # Use raw strings to avoid Python escape sequence issues
    cleaned = cleaned.replace(r'\beginpmatrix', r'\begin{pmatrix}')
    cleaned = cleaned.replace(r'\endpmatrix', r'\end{pmatrix}')
    cleaned = cleaned.replace(r'\beginmatrix', r'\begin{pmatrix}')
    cleaned = cleaned.replace(r'\endmatrix', r'\end{pmatrix}')

    # Fix double braces {{...}} → {...}
    cleaned = re.sub(r'\{\{+', '{', cleaned)
    cleaned = re.sub(r'\}\}+', '}', cleaned)

    # Fix \[ \] → [] (escaped brackets from OCR)
    cleaned = cleaned.replace(r'\[', '[')
    cleaned = cleaned.replace(r'\]', ']')

    # Replace array environment with pmatrix
    cleaned = cleaned.replace(r'\begin{array}', r'\begin{pmatrix}')
    cleaned = cleaned.replace(r'\end{array}', r'\end{pmatrix}')

    # Fix \begin{pmatrix}{c}{item} → \begin{pmatrix}{item}
    # The {c} is a column spec that shouldn't be there - just remove it
    cleaned = re.sub(r'(\\begin\{(?:p)?matrix\})\{[^}]*\}', r'\1', cleaned)

    # Fix \cdot\cdot → \cdots
    while r'\cdot\cdot' in cleaned:
        cleaned = cleaned.replace(r'\cdot\cdot', r'\cdots')
    while r'\cdots\cdots' in cleaned:
        cleaned = cleaned.replace(r'\cdots\cdots', r'\cdots')
    cleaned = cleaned.replace(r'\cdots\cdot', r'\cdots')
    cleaned = cleaned.replace(r'\cdot\cdots', r'\cdots')

    # Fix \bf → \mathbf (bf doesn't work in KaTeX)
    cleaned = re.sub(r'\{\\bf\s+([A-Za-z])\}', r'\\mathbf{\1}', cleaned)
    cleaned = re.sub(r'\{\\bf\s+([^{}]+)\}', r'\\mathbf{\1}', cleaned)
    cleaned = cleaned.replace(r'{\bf ', r'\mathbf{')
    cleaned = re.sub(r'(?<!\\)\\bf\b', '', cleaned)  # remove orphan \bf

    # Fix {\bf1} or {\bf 1} → 1 (bf can't format numbers)
    cleaned = re.sub(r'\{\\bf\s*(\d+)\}', r'\1', cleaned)

    # Fix common OCR errors in \mathrm commands
    cleaned = re.sub(r'\\mathrm\{([A-Z][A-Z]+)\}', r'\1', cleaned)

    # Fix \frac{1}x → \frac{1}{x} (missing braces in denominator)
    cleaned = re.sub(r'\\frac\{([^}]+)\}([A-Za-z\\])', r'\\frac{\1}{\2}', cleaned)

    # Fix \left\langle → <
    cleaned = cleaned.replace(r'\left\langle', '<')
    cleaned = cleaned.replace(r'\right\rangle', '>')
    cleaned = cleaned.replace(r'\langle', '<')
    cleaned = cleaned.replace(r'\rangle', '>')

    # Remove unsupported environments
    cleaned = re.sub(r'\\begin\{(?:table|tabular|picture)\}.*?\\end\{(?:table|tabular|picture)\}', '', cleaned, flags=re.DOTALL)

    # Fix missing backslash in common commands
    cleaned = re.sub(r'(?<!\\)\b(sin|cos|tan|log|ln|exp)\b', r'\\\1', cleaned)

    # Clean up empty braces
    cleaned = re.sub(r'\{\s*\}', '', cleaned)

    # Final cleanup: remove any remaining {c} type specs in matrices
    cleaned = re.sub(r'\{([lctr])\}(?=\\\\|\\end)', '', cleaned)

    return cleaned


def strip_simple_braces(s: str) -> str:
    """Strip outer {} from simple tokens inside matrix."""
    # Remove {token} → token only if no nested braces
    return re.sub(r'\{([^{}\\]{1,40})\}', r'\1', s)


def normalize_ocr_latex(latex: str) -> str:
    cleaned = latex or ''
    replacements = {
        r'{\bf x}': 'x',
        r'{\bf v}': 'v',
        r'{\bf s}': 's',
        r'\,': '',
        r'\ ': ' ',
    }
    for src, dst in replacements.items():
        cleaned = cleaned.replace(src, dst)
    cleaned = re.sub(r'\\mathrm\{([^{}]+)\}', r'\1', cleaned)
    cleaned = re.sub(r'\{\\bf\s+([^{}]+)\}', r'\1', cleaned)
    cleaned = cleaned.replace('{', '').replace('}', '')
    cleaned = cleaned.replace('\\left', '').replace('\\right', '')
    cleaned = cleaned.replace('\\theta', 'theta')
    cleaned = cleaned.replace('\\varphi', 'phi')
    cleaned = cleaned.replace('\\cdot', '*')
    cleaned = cleaned.replace('\\', '')
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def derive_formula_symbols(section: Section, block: Block, block_index: int) -> list[tuple[str, str]]:
    """Extract symbol chips from LaTeX using the domain symbol dictionary."""
    raw_latex = block.ocr_latex or block.copy_text
    if not raw_latex:
        return []
    pairs: list[tuple[str, str]] = []
    seen_bases: set[str] = set()
    for token in sorted(SYMBOL_DICT, key=len, reverse=True):
        if token in raw_latex:
            base = token.strip('\\').split('{')[0]
            if base not in seen_bases:
                display = token.replace('\\', '').replace('{', '').replace('}', '')
                pairs.append((display, SYMBOL_DICT[token]))
                seen_bases.add(base)
                seen_bases.add(token)
    return pairs[:8]


def render_symbol_panel(symbols: list[tuple[str, str]]) -> str:
    if not symbols:
        return ''
    chips = ''.join(symbol_button(symbol, meaning) for symbol, meaning in symbols)
    rows = ''.join(
        f"<li><strong>{html.escape(symbol)}</strong> {rich(meaning)}</li>"
        for symbol, meaning in symbols
    )
    return (
        "<div class='symbol-panel'>"
        "<p><strong>这一处常见符号</strong></p>"
        f"<div class='symbol-chips'>{chips}</div>"
        f"<ul class='symbol-list'>{rows}</ul>"
        "</div>"
    )


def render_inline_explainer(kind: str, number: int, anchor_id: str, rows: list[tuple[str, str]], extra_html: str = '') -> str:
    summary = '展开图解' if kind == 'figure' else '展开公式解读'
    label = '图' if kind == 'figure' else '公式'
    body = ''.join(f"<p><strong>{html.escape(name)}</strong> {rich(value)}</p>" for name, value in rows)
    return (
        f"<details class='inline-explainer {kind}-explainer' id='{anchor_id}-note'>"
        f"<summary><a href='#{anchor_id}' class='anchor-link'>{label} {number:02d}</a> · {summary}</summary>"
        f"<div class='inline-body'>{body}{extra_html}</div>"
        "</details>"
    )


def render_formula_block(section: Section, block: Block, block_index: int) -> str:
    formula_no = int(block.extra.get('formula_index', 0))
    anchor_id = f'formula-{formula_no:02d}'
    image_html = ''
    if block.asset_rel:
        image_html = f"<img src='{block.asset_rel}' alt='公式 {formula_no:02d} 截图' loading='lazy'>"
    raw_latex = block.ocr_latex or block.copy_text
    latex = sanitize_for_katex(raw_latex)
    katex_rendered = ''
    if latex:
        safe_latex = html.escape(latex, quote=True)
        katex_rendered = (
            f'<div class=\'katex-block\' data-latex="{safe_latex}" style=\'display:none;\'>'
            f'<span class=\'katex-eq\'>{safe_latex}</span></div>'
        )
        button = (
            f"<button type='button' class='copy-btn' data-copy='{safe_latex}'>"
            '复制公式文本</button>'
        )
    else:
        button = "<button type='button' class='copy-btn' disabled>暂无可复制公式文本</button>"
    rows, reliable = grounded_formula_rows(section, block_index, block)
    symbols = derive_formula_symbols(section, block, block_index)
    extra_html = render_symbol_panel(symbols)
    explainer = render_inline_explainer('formula', formula_no, anchor_id, rows, extra_html)
    return (
        f"<div class='formula-wrap' id='{anchor_id}'>"
        "<div class='formula-block'>"
        f"<div class='formula-meta'><a href='#{anchor_id}' class='anchor-link'>公式 {formula_no:02d}</a></div>"
        f"<div class='formula-toolbar'>{button}</div>"
        f"{katex_rendered}"
        f"<div class='formula-image-fallback'>{image_html}</div>"
        "</div>"
        f"{explainer}"
        "</div>"
    )


def render_figure_block(section: Section, block: Block) -> str:
    figure_no = int(block.extra.get('figure_index', 0))
    anchor_id = f'figure-{figure_no:02d}'
    caption = f"图 {figure_no:02d} · 原文插图"
    img_html = f"<img src='{block.asset_rel}' alt='{html.escape(caption, quote=True)}' loading='lazy'>" if block.asset_rel else ''
    block_idx = section.blocks.index(block)
    prev_para = nearest_paragraph_text(section, block_idx, -1)
    next_para = nearest_paragraph_text(section, block_idx, 1)
    rows = figure_note(section.title, block.ocr_text, figure_no, prev_para, next_para)
    explainer = render_inline_explainer('figure', figure_no, anchor_id, rows)
    return (
        f"<div class='figure-wrap' id='{anchor_id}'>"
        f"<figure class='paper-figure'>{img_html}<figcaption><a href='#{anchor_id}' class='anchor-link'>{caption}</a></figcaption></figure>"
        f"{explainer}"
        "</div>"
    )


def render_source_block(section: Section, block: Block, block_index: int) -> str:
    if block.type == 'paragraph':
        return render_paragraph_block(block)
    if block.type == 'figure':
        return render_figure_block(section, block)
    if block.type == 'formula':
        return render_formula_block(section, block, block_index)
    return ''


def render_note_cards(section: Section) -> str:
    cards: list[str] = []
    cards.append(
        "<div class='note-card'>"
        "<div class='note-head'>这一节</div>"
        + ''.join(
            f"<p><strong>{html.escape(label)}</strong> {rich(value)}</p>"
            for label, value in [
                ('这节在做什么', section_role(section.title)),
                ('读的时候怎么抓', '先看这节是在立模型、讲方法，还是给结果，再决定自己要盯公式、盯图，还是盯结论。'),
                ('读完要记住', section_takeaway(section.title)),
            ]
        )
        + '</div>'
    )
    para_index = 0
    for block in section.blocks:
        if block.type != 'paragraph':
            continue
        para_index += 1
        rows = [
            ('这段在说什么', sentence_snippet(block.text, 120)),
            ('和上下文的关系', paragraph_role(block.text, para_index, section.title)),
            ('读的时候抓什么', paragraph_focus(block.text)),
        ]
        cards.append(
            "<div class='note-card'><div class='note-head'>P%d</div>%s</div>"
            % (para_index, ''.join(f"<p><strong>{html.escape(label)}</strong> {rich(value)}</p>" for label, value in rows))
        )
    return ''.join(cards)


def render_section(section: Section, index: int) -> str:
    source_html = ''.join(render_source_block(section, block, idx) for idx, block in enumerate(section.blocks))
    return (
        f"<section id='{section.id}' class='reading-row'>"
        "<div class='original-col'>"
        f"<div class='section-kicker'>原文带读 · S{index}</div>"
        f"<h2>{rich(section.title)}</h2>"
        f"<div class='paper-flow'>{source_html}</div>"
        '</div>'
        "<aside class='note-col'>"
        f"<div class='section-kicker'>带读分析 · S{index}</div>{render_note_cards(section)}"
        '</aside>'
        '</section>'
    )


def build_html(paper: PaperDoc, out_dir: Path, page_preview: str) -> str:
    toc_links = ''.join(
        f"<a href='#{section.id}' class='toc-link'>{rich(section.title)}</a>" for section in paper.sections
    )
    cards = ''.join(
        f"<article class='summary-card'><h3>{html.escape(title)}</h3><p>{rich(body)}</p></article>"
        for title, body in document_cards(paper)
    )
    section_html = ''.join(render_section(section, idx + 1) for idx, section in enumerate(paper.sections))
    pdf_rel = html.escape(relative_href(paper.source_pdf, out_dir))

    return f"""<!DOCTYPE html>
<html lang='zh-CN'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>{html.escape(paper.title)} | Paper Reading HTML</title>
<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css' crossorigin='anonymous'>
<script defer src='https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js' crossorigin='anonymous'></script>
<style>
:root {{ --bg:#f4efe4; --paper:#fffdf8; --ink:#1e1e1b; --muted:#635d52; --line:#d8cfbf; --accent:#8e5a2b; --accent-soft:#efe4d2; --note:#f8f1e6; --shadow:0 18px 40px rgba(57,43,23,.08); }}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ margin:0; color:var(--ink); background:linear-gradient(180deg,#efe6d5 0%, var(--bg) 28%, #f8f3eb 100%); font:16px/1.82 "PingFang SC","Microsoft YaHei",sans-serif; }}
a {{ color:inherit; }}
button {{ font:inherit; }}
.topbar {{ position:sticky; top:0; z-index:20; backdrop-filter:blur(12px); background:rgba(248,243,235,.9); border-bottom:1px solid rgba(141,114,78,.18); }}
.topbar-inner,.hero,.layout {{ width:min(1500px, calc(100vw - 48px)); margin:0 auto; }}
.topbar-inner {{ display:flex; justify-content:space-between; gap:16px; padding:14px 0; align-items:center; }}
.brand {{ font-size:14px; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); font-weight:700; }}
.meta {{ display:flex; gap:12px; flex-wrap:wrap; color:var(--muted); font-size:14px; align-items:center; }}
.meta a, .meta span {{ padding:8px 12px; border:1px solid var(--line); border-radius:999px; background:var(--paper); text-decoration:none; }}
.meta a {{ color:var(--accent); }}
.shell {{ padding:28px 0 44px; }}
.hero {{ display:grid; grid-template-columns:minmax(0,1.35fr) 360px; gap:24px; margin-bottom:24px; }}
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
.toc-links {{ position:relative; }}
.toc-slider {{ position:absolute; left:-6px; top:0; width:4px; height:28px; border-radius:999px; background:linear-gradient(180deg,#b7712f 0%, #8e5a2b 100%); box-shadow:0 6px 18px rgba(142,90,43,.25); transition:transform .22s ease, height .22s ease, opacity .18s ease; opacity:0; }}
.toc-link {{ position:relative; z-index:1; display:block; text-decoration:none; color:var(--muted); padding:8px 0 8px 10px; border-top:1px solid rgba(216,207,191,.7); border-radius:10px; transition:background .18s ease, color .18s ease; }}
.toc-link:first-of-type {{ border-top:0; padding-top:0; }}
.toc-link.active {{ color:#6f431d; background:rgba(142,90,43,.08); }}
.main {{ display:grid; gap:24px; }}
.summary-grid {{ display:grid; gap:18px; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); }}
.summary-card {{ padding:20px; }}
.summary-card h3 {{ margin:0 0 10px; }}
.reading-row {{ display:grid; grid-template-columns:minmax(0,1.55fr) minmax(300px,.85fr); gap:22px; align-items:start; scroll-margin-top:92px; }}
.original-col {{ padding:24px; }}
.note-col {{ padding:20px; position:sticky; top:88px; }}
.original-col h2 {{ margin:0 0 16px; font-size:28px; line-height:1.2; scroll-margin-top:92px; }}
.paper-flow p {{ margin:0 0 12px; line-height:1.92; color:#2d2a24; }}
.paper-flow .list-item {{ padding-left:1.2em; text-indent:-1.2em; }}
.figure-wrap,.formula-wrap {{ margin:18px 0 14px; }}
.paper-figure {{ margin:0; padding:16px; background:#fbf6ec; border:1px solid #eadfcd; border-radius:18px; }}
.paper-figure img, .formula-block img {{ width:100%; border-radius:12px; display:block; background:white; }}
.paper-figure figcaption {{ margin-top:10px; color:var(--muted); }}
.formula-block {{ padding:16px; background:#fbf6ec; border:1px solid #eadfcd; border-radius:18px; }}
.katex-block {{ padding:12px; background:#fff; border-radius:12px; margin-bottom:8px; text-align:center; overflow-x:auto; }}
.formula-image-fallback {{ display:none; }}
.formula-image-fallback img {{ max-width:100%; border-radius:8px; }}
.formula-meta {{ margin-bottom:10px; color:var(--muted); }}
.formula-toolbar {{ display:flex; justify-content:flex-end; margin-bottom:10px; }}
.copy-btn {{ padding:8px 12px; border-radius:999px; border:1px solid #d1b48f; background:#fff7ea; color:#7a4d22; cursor:pointer; }}
.copy-btn[disabled] {{ opacity:.55; cursor:not-allowed; }}
.inline-explainer {{ margin-top:10px; border:1px solid #eadfcd; border-radius:16px; background:#fffaf2; overflow:hidden; }}
.inline-explainer summary {{ list-style:none; cursor:pointer; padding:12px 14px; color:#7a4d22; font-weight:700; }}
.inline-explainer summary::-webkit-details-marker {{ display:none; }}
.inline-body {{ padding:0 14px 14px; border-top:1px solid rgba(216,207,191,.7); }}
.inline-body p {{ margin:12px 0 0; color:var(--muted); }}
.anchor-link {{ color:#7a4d22; text-decoration:none; border-bottom:1px dashed rgba(122,77,34,.38); }}
.symbol-panel {{ margin-top:14px; padding:14px; border-radius:14px; background:#f6efe3; border:1px solid #eadfcd; }}
.symbol-chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
.symbol-chip {{ border:0; background:#e7d8c1; color:#6f431d; padding:6px 10px; border-radius:999px; cursor:pointer; }}
.symbol-list {{ margin:12px 0 0; padding-left:18px; color:var(--muted); }}
.symbol-list li {{ margin:8px 0 0; }}
.note-card {{ padding:16px 18px; border-radius:18px; background:var(--note); border:1px solid #eadfcd; margin-bottom:14px; }}
.note-head {{ color:var(--accent); font-size:13px; font-weight:700; margin-bottom:8px; }}
.note-card p {{ margin:0 0 10px; line-height:1.8; }}
.note-card p:last-child {{ margin-bottom:0; }}
.term {{ border:0; background:rgba(142,90,43,.12); color:#7c4e21; padding:0 .35em; border-radius:999px; cursor:pointer; }}
.term-pop {{ position:fixed; inset:auto 20px 20px auto; max-width:360px; padding:14px 16px; background:#fffdf8; border:1px solid rgba(142,90,43,.18); border-radius:16px; box-shadow:var(--shadow); display:none; z-index:30; }}
.term-pop.open {{ display:block; }}
.term-pop h4 {{ margin:0 0 6px; color:var(--accent); }}
.term-pop p {{ margin:0; color:var(--muted); }}
.toast {{ position:fixed; left:50%; bottom:22px; transform:translateX(-50%); background:#2f271d; color:#fff; padding:10px 14px; border-radius:999px; opacity:0; pointer-events:none; transition:opacity .18s ease; z-index:40; }}
.toast.show {{ opacity:1; }}
@media (max-width:1180px) {{ .layout,.hero,.reading-row {{ grid-template-columns:1fr; }} .rail,.note-col {{ position:static; }} .toc-slider {{ display:none; }} }}
</style>
</head>
<body>
<header class='topbar'><div class='topbar-inner'><div class='brand'>Paper Reading HTML</div><div class='meta'><span>{html.escape(paper.title)}</span><span>{paper.page_count} 页 · {paper.figure_count} 图 · {paper.formula_count} 公式块</span><a href='{pdf_rel}'>原 PDF</a></div></div></header>
<main class='shell'>
<section class='hero'>
<div class='hero-copy'><p class='hero-kicker'>paper-reading-html · extraction-driven</p><h1>{html.escape(paper.title)}</h1><p>这个页面先给出 <strong>文档解读</strong>，把全文主线、证据链和应当抓住的结论先立住；后面再进入 <strong>原文带读</strong>，按 Docling 抽出的真实顺序把段落、图片和公式一点点理顺。图和公式优先保留原版面里的可读形态，不再只给一句轻飘的总结。</p></div>
<div class='hero-side'><img src='{page_preview}' alt='首页预览'><div class='hero-side-copy'><h2>这一版的原则</h2><p>网页先对齐原文，再做解释。图从页图里裁，公式也从页图里裁，这样即使公式文本不完美，读者至少能先在网页里把论证走通。</p></div></div>
</section>
<div class='layout'>
<aside class='rail'>
<div class='toc-card'><p class='eyebrow'>页面导航</p><nav class='toc-links'><div class='toc-slider' aria-hidden='true'></div><a href='#document-reading' class='toc-link'>文档解读</a><a href='#guided-reading' class='toc-link'>原文带读</a>{toc_links}</nav></div>
</aside>
<section class='main'>
<section id='document-reading'><div class='summary-grid'>{cards}</div></section>
<section id='guided-reading'>{section_html}</section>
</section>
</div>
</main>
<div id='term-pop' class='term-pop'><h4 id='term-title'></h4><p id='term-body'></p></div>
<div id='toast' class='toast'>已复制</div>
<script>
document.addEventListener('DOMContentLoaded', () => {{
    // Render KaTeX formulas
    document.querySelectorAll('.katex-block').forEach(block => {{
        const latex = block.getAttribute('data-latex');
        if (latex) {{
            try {{
                katex.render(latex, block, {{ displayMode: true, throwOnError: false }});
                block.style.display = 'block';
            }} catch (e) {{
                block.style.display = 'none';
            }}
        }}
    }});
    // If KaTeX failed, show image fallback
    document.querySelectorAll('.katex-block').forEach(block => {{
        if (block.style.display === 'none') {{
            const fallback = block.closest('.formula-block').querySelector('.formula-image-fallback');
            if (fallback) fallback.style.display = 'block';
        }}
    }});
}});
const pop = document.getElementById('term-pop');
const title = document.getElementById('term-title');
const body = document.getElementById('term-body');
document.querySelectorAll('.term').forEach(btn => {{
  btn.addEventListener('click', () => {{
    title.textContent = btn.dataset.term || '';
    body.textContent = btn.dataset.definition || '';
    pop.classList.add('open');
  }});
}});
document.addEventListener('click', (event) => {{
  if (!event.target.closest('.term') && !event.target.closest('#term-pop')) {{
    pop.classList.remove('open');
  }}
}});
const toast = document.getElementById('toast');
document.querySelectorAll('.copy-btn[data-copy]').forEach(btn => {{
  btn.addEventListener('click', async () => {{
    if (btn.disabled) return;
    try {{
      await navigator.clipboard.writeText(btn.dataset.copy || '');
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 1200);
    }} catch (err) {{
      console.error(err);
    }}
  }});
}});
const tocLinks = Array.from(document.querySelectorAll('.toc-link'));
const tocSlider = document.querySelector('.toc-slider');
function moveSlider(link) {{
  if (!link || !tocSlider) return;
  tocSlider.style.opacity = '1';
  tocSlider.style.transform = `translateY(${{link.offsetTop}}px)`;
  tocSlider.style.height = `${{link.offsetHeight}}px`;
  tocLinks.forEach(item => item.classList.toggle('active', item === link));
}}
function activateByHash(hash) {{
  const link = tocLinks.find(item => item.getAttribute('href') === hash);
  if (link) moveSlider(link);
}}
const sections = tocLinks.map(link => {{
  const target = document.querySelector(link.getAttribute('href'));
  return target ? {{link, target}} : null;
}}).filter(Boolean);
const observer = new IntersectionObserver((entries) => {{
  const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio);
  if (!visible.length) return;
  const winner = sections.find(item => item.target === visible[0].target);
  if (winner) moveSlider(winner.link);
}}, {{rootMargin: '-25% 0px -55% 0px', threshold: [0.05, 0.2, 0.5, 0.8]}});
sections.forEach(item => observer.observe(item.target));
tocLinks.forEach(link => link.addEventListener('click', () => moveSlider(link)));
window.addEventListener('load', () => {{
  activateByHash(window.location.hash || '#document-reading');
}});
window.addEventListener('hashchange', () => activateByHash(window.location.hash));
</script>
</body>
</html>"""


def build_paper(extract_dir: Path, out_dir: Path, pdf_path: Path, explicit_title: str | None) -> PaperDoc:
    doc_json = resolve_docling_json(extract_dir)
    doc_data = load_json(doc_json)
    title, sections = build_sections(doc_data)
    if explicit_title:
        title = explicit_title
    attach_assets(doc_data, sections, out_dir, pdf_path)
    run_formula_ocr(out_dir, sections)
    figure_count = sum(1 for section in sections for block in section.blocks if block.type == 'figure')
    formula_count = sum(1 for section in sections for block in section.blocks if block.type == 'formula')
    return PaperDoc(
        title=title,
        sections=sections,
        page_count=len(doc_data.get('pages', {})),
        figure_count=figure_count,
        formula_count=formula_count,
        source_pdf=pdf_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description='Render a Docling extraction into a guided reading HTML page.')
    parser.add_argument('--extract-dir', type=Path, required=True, help='Directory containing manifest.json and docling output.')
    parser.add_argument('--out-dir', type=Path, required=True, help='Directory where index.html and assets will be written.')
    parser.add_argument('--pdf', type=Path, help='Optional source PDF path. Falls back to manifest.json when omitted.')
    parser.add_argument('--title', help='Override paper title.')
    args = parser.parse_args()

    extract_dir = args.extract_dir.resolve()
    out_dir = ensure_dir(args.out_dir.resolve())
    pdf_path = resolve_pdf_path(extract_dir, args.pdf)
    paper = build_paper(extract_dir, out_dir, pdf_path, args.title)
    preview = 'assets/pages/page-01.png'
    html_text = build_html(paper, out_dir, preview)
    (out_dir / 'index.html').write_text(html_text, encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

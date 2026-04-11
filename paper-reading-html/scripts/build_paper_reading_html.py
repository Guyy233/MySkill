from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable


def run(script: str, args: list[str] | None = None) -> None:
    cmd = [PYTHON, str(SCRIPT_DIR / script)] + (args or [])
    subprocess.run(cmd, check=True)


def render_repro_pages() -> None:
    workspace_root = Path.cwd()
    repro_root = workspace_root / '结题' / 'document' / 'repro'
    repro_html_root = repro_root / 'paper2web'
    run(
        'render_docling_guided_html.py',
        [
            '--extract-dir',
            str(repro_html_root / 'extracted' / 'spatial-anti-jamming'),
            '--out-dir',
            str(repro_html_root / 'spatial-anti-jamming'),
            '--pdf',
            str(repro_root / '空域抗干扰算法.pdf'),
        ],
    )
    run(
        'render_docling_guided_html.py',
        [
            '--extract-dir',
            str(repro_html_root / 'extracted' / 'spatial-filter-simulation'),
            '--out-dir',
            str(repro_html_root / 'spatial-filter-simulation'),
            '--pdf',
            str(repro_root / '空域滤波算法仿真.pdf'),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description='paper-reading-html 统一入口：抽取 PDF、渲染全文带读网页、重建 repro 页面。'
    )
    sub = parser.add_subparsers(dest='command', required=True)

    extract = sub.add_parser('extract', help='运行 PDF 抽取流水线，产出 Docling / Marker 等结构化产物。')
    extract.add_argument('pdf', help='输入 PDF 路径')
    extract.add_argument('--out-dir', required=True, help='抽取产物输出目录')
    extract.add_argument('--render-pages', action='store_true', help='额外渲染整页预览')

    render_docling = sub.add_parser('render-docling', help='把 Docling 抽取结果渲染成全文带读 HTML。')
    render_docling.add_argument('--extract-dir', required=True, help='包含 manifest.json 和 docling 输出的目录')
    render_docling.add_argument('--out-dir', required=True, help='网页输出目录')
    render_docling.add_argument('--pdf', help='可选，显式传入源 PDF 路径')
    render_docling.add_argument('--title', help='可选，覆盖页面标题')

    from_pdf = sub.add_parser('from-pdf', help='从 PDF 一步生成结构化抽取 + 全文带读 HTML。')
    from_pdf.add_argument('pdf', help='输入 PDF 路径')
    from_pdf.add_argument('--extract-dir', required=True, help='抽取产物输出目录')
    from_pdf.add_argument('--out-dir', required=True, help='网页输出目录')
    from_pdf.add_argument('--title', help='可选，覆盖页面标题')
    from_pdf.add_argument('--render-pages', action='store_true', help='抽取阶段额外渲染整页预览')

    sub.add_parser('repro', help='重建 repro 三篇论文网页。')
    sub.add_parser('first-paper', help='用 extraction-driven 深度模板重跑第一篇。')
    sub.add_parser('all', help='先重建 repro 三篇，再重跑第一篇深度版。')

    args = parser.parse_args()

    if args.command == 'extract':
        extra = [args.pdf, '--out-dir', args.out_dir]
        if args.render_pages:
            extra.append('--render-pages')
        run('extract_pdf_pipeline.py', extra)
        return

    if args.command == 'render-docling':
        extra = ['--extract-dir', args.extract_dir, '--out-dir', args.out_dir]
        if args.pdf:
            extra.extend(['--pdf', args.pdf])
        if args.title:
            extra.extend(['--title', args.title])
        run('render_docling_guided_html.py', extra)
        return

    if args.command == 'from-pdf':
        extract_args = [args.pdf, '--out-dir', args.extract_dir]
        if args.render_pages:
            extract_args.append('--render-pages')
        run('extract_pdf_pipeline.py', extract_args)
        render_args = ['--extract-dir', args.extract_dir, '--out-dir', args.out_dir, '--pdf', args.pdf]
        if args.title:
            render_args.extend(['--title', args.title])
        run('render_docling_guided_html.py', render_args)
        return

    if args.command == 'repro':
        run('rebuild_repro_reading_pages.py')
        render_repro_pages()
        run('build_first_paper_rerun.py')
        return

    if args.command == 'first-paper':
        run('build_first_paper_rerun.py')
        return

    if args.command == 'all':
        run('rebuild_repro_reading_pages.py')
        render_repro_pages()
        run('build_first_paper_rerun.py')


if __name__ == '__main__':
    main()

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any


def get_extra_sites() -> list[str]:
    extra = os.environ.get('PAPER_READING_HTML_EXTRA_SITE', '').strip()
    if not extra:
        return []
    sites: list[str] = []
    for raw in extra.split(os.pathsep):
        candidate = raw.strip()
        if candidate:
            sites.append(candidate)
    return sites


def bootstrap_extra_site() -> None:
    for candidate in reversed(get_extra_sites()):
        if candidate not in sys.path:
            sys.path.insert(0, candidate)


bootstrap_extra_site()


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8')


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def list_files(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(str(item) for item in path.rglob('*') if item.is_file())


def safe_stem(name: str) -> str:
    normalized = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    cleaned = ''.join(ch if ch.isalnum() else '-' for ch in normalized).strip('-').lower()
    cleaned = '-'.join(part for part in cleaned.split('-') if part)
    if cleaned:
        return cleaned
    digest = hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
    return f'paper-{digest}'


def summarize_process(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        'returncode': result.returncode,
        'stdout_tail': result.stdout[-4000:],
        'stderr_tail': result.stderr[-4000:],
    }


def build_subprocess_env(extra_sites_override: list[str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    extra_sites = extra_sites_override if extra_sites_override is not None else get_extra_sites()
    if extra_sites:
        existing = env.get('PYTHONPATH', '').strip()
        env['PYTHONPATH'] = os.pathsep.join(extra_sites + ([existing] if existing else []))
    return env


def run_subprocess(
    command: list[str],
    *,
    cwd: Path | None = None,
    extra_sites_override: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = build_subprocess_env(extra_sites_override)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )


def find_site_with_package(package_dir: str) -> str | None:
    for site in get_extra_sites():
        if (Path(site) / package_dir).exists():
            return site
    return None


def get_docling_site() -> str | None:
    return find_site_with_package('docling')


def get_marker_site() -> str | None:
    env_bin = os.environ.get('PAPER_READING_HTML_MARKER_BIN', '').strip()
    if env_bin:
        path = Path(env_bin)
        if path.exists():
            candidate = path.parent.parent
            if candidate.exists():
                return str(candidate)
    return find_site_with_package('marker')


def get_marker_cache_dir() -> str:
    override = os.environ.get('PAPER_READING_HTML_MARKER_CACHE', '').strip()
    if override:
        ensure_dir(Path(override))
        return override
    cache_dir = Path(r'D:\study\A_finalyear_prj\.cache\paper-reading-html\marker-models')
    ensure_dir(cache_dir)
    return str(cache_dir)


def get_marker_temp_dir() -> str:
    override = os.environ.get('PAPER_READING_HTML_MARKER_TEMP', '').strip()
    if override:
        ensure_dir(Path(override))
        return override
    temp_dir = Path(r'D:\study\A_finalyear_prj\.cache\paper-reading-html\marker-temp')
    ensure_dir(temp_dir)
    return str(temp_dir)


def get_marker_command() -> str | None:
    env_candidate = os.environ.get('PAPER_READING_HTML_MARKER_BIN', '').strip()
    if env_candidate and Path(env_candidate).exists():
        return env_candidate

    direct = shutil.which('marker_single')
    if direct:
        return direct

    marker_site = get_marker_site()
    if marker_site:
        for relative in ('bin/marker_single.exe', 'bin/marker_single', 'Scripts/marker_single.exe'):
            candidate = Path(marker_site) / relative
            if candidate.exists():
                return str(candidate)
    return None


def probe_backends() -> dict[str, Any]:
    return {
        'modules': {
            'docling': module_available('docling'),
            'marker': module_available('marker'),
            'pymupdf4llm': module_available('pymupdf4llm'),
            'fitz': module_available('fitz'),
            'rapid_latex_ocr': module_available('rapid_latex_ocr'),
        },
        'commands': {
            'docling': command_available('docling'),
            'marker_single': bool(get_marker_command()),
            'mineru': command_available('mineru'),
            'pdfimages': command_available('pdfimages'),
            'pdftoppm': command_available('pdftoppm'),
            'java': command_available('java'),
        },
        'environment': {
            'python': sys.executable,
            'platform': sys.platform,
            'extra_sites': get_extra_sites(),
            'docling_site': get_docling_site(),
            'marker_site': get_marker_site(),
            'marker_bin': get_marker_command(),
            'marker_cache_dir': get_marker_cache_dir(),
        },
    }


def export_docling(pdf_path: Path, backend_dir: Path) -> dict[str, Any]:
    if not module_available('docling'):
        return {
            'status': 'missing_dependency',
            'backend': 'docling',
            'message': 'Install docling first: pip install docling',
        }

    from extract_with_docling import export_docling as export_with_docling

    return export_with_docling(pdf_path, backend_dir)


def export_marker(pdf_path: Path, backend_dir: Path) -> dict[str, Any]:
    marker_command = get_marker_command()
    marker_site = get_marker_site()
    if not marker_command or not marker_site:
        return {
            'status': 'missing_dependency',
            'backend': 'marker',
            'message': 'Install marker first: pip install marker-pdf, then set PAPER_READING_HTML_MARKER_BIN if needed.',
        }

    formats = ('markdown', 'json', 'html')
    results: dict[str, Any] = {}
    overall_ok = False

    for output_format in formats:
        format_dir = ensure_dir(backend_dir / output_format)
        cmd = [
            marker_command,
            str(pdf_path),
            '--output_format',
            output_format,
            '--output_dir',
            str(format_dir),
            '--disable_multiprocessing',
            '--disable_tqdm',
        ]
        completed = run_subprocess(
            cmd,
            extra_sites_override=[marker_site],
            extra_env={
                'MODEL_CACHE_DIR': get_marker_cache_dir(),
                'TMP': get_marker_temp_dir(),
                'TEMP': get_marker_temp_dir(),
                'TMPDIR': get_marker_temp_dir(),
            },
        )
        results[output_format] = {
            'status': 'ok' if completed.returncode == 0 else 'error',
            'process': summarize_process(completed),
            'files': list_files(format_dir),
        }
        overall_ok = overall_ok or completed.returncode == 0

    return {
        'status': 'ok' if overall_ok else 'error',
        'backend': 'marker',
        'marker_command': marker_command,
        'marker_site': marker_site,
        'outputs': results,
    }


def export_mineru(pdf_path: Path, backend_dir: Path, backend_name: str) -> dict[str, Any]:
    if not command_available('mineru'):
        return {
            'status': 'missing_dependency',
            'backend': 'mineru',
            'message': 'Install MinerU first: uv pip install -U "mineru[all]"',
        }

    cmd = [shutil.which('mineru') or 'mineru', '-p', str(pdf_path), '-o', str(backend_dir)]
    if backend_name:
        cmd.extend(['-b', backend_name])

    completed = run_subprocess(cmd)
    return {
        'status': 'ok' if completed.returncode == 0 else 'error',
        'backend': 'mineru',
        'process': summarize_process(completed),
        'files': list_files(backend_dir),
    }


def export_pdfimages(pdf_path: Path, backend_dir: Path, render_pages: bool) -> dict[str, Any]:
    if not command_available('pdfimages'):
        return {
            'status': 'missing_dependency',
            'backend': 'pdfimages',
            'message': 'pdfimages is not available on PATH.',
        }

    base_name = safe_stem(pdf_path.stem)
    images_dir = ensure_dir(backend_dir / 'embedded')
    staging_root = ensure_dir(Path(tempfile.gettempdir()) / 'paper-reading-html' / f'pdfimages-{base_name}')
    if staging_root.exists():
        shutil.rmtree(staging_root, ignore_errors=True)
    ensure_dir(staging_root)
    prefix = staging_root / base_name
    extract_cmd = [shutil.which('pdfimages') or 'pdfimages', '-png', str(pdf_path), str(prefix)]
    extract_completed = run_subprocess(extract_cmd)

    for item in staging_root.glob(f'{base_name}-*.png'):
        shutil.move(str(item), images_dir / item.name)

    list_cmd = [shutil.which('pdfimages') or 'pdfimages', '-list', str(pdf_path)]
    list_completed = run_subprocess(list_cmd)
    write_text(backend_dir / 'pdfimages-list.txt', list_completed.stdout)

    page_raster: dict[str, Any] | None = None
    if render_pages and command_available('pdftoppm'):
        pages_dir = ensure_dir(backend_dir / 'pages')
        raster_stage = ensure_dir(Path(tempfile.gettempdir()) / 'paper-reading-html' / f'pdftoppm-{base_name}')
        if raster_stage.exists():
            shutil.rmtree(raster_stage, ignore_errors=True)
        ensure_dir(raster_stage)
        raster_cmd = [
            shutil.which('pdftoppm') or 'pdftoppm',
            '-png',
            str(pdf_path),
            str(raster_stage / base_name),
        ]
        raster_completed = run_subprocess(raster_cmd)
        for item in raster_stage.glob(f'{base_name}-*.png'):
            shutil.move(str(item), pages_dir / item.name)
        page_raster = {
            'status': 'ok' if raster_completed.returncode == 0 else 'error',
            'process': summarize_process(raster_completed),
            'files': list_files(pages_dir),
        }

    shutil.rmtree(staging_root, ignore_errors=True)

    return {
        'status': 'ok' if extract_completed.returncode == 0 else 'error',
        'backend': 'pdfimages',
        'source_name': pdf_path.name,
        'artifact_base_name': base_name,
        'embedded_images': {
            'process': summarize_process(extract_completed),
            'files': list_files(images_dir),
        },
        'image_list_path': str(backend_dir / 'pdfimages-list.txt'),
        'page_raster': page_raster,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Run the paper-reading-html extraction stack with the best available backends.'
    )
    parser.add_argument('pdf', type=Path, help='Path to the source PDF')
    parser.add_argument('--out-dir', type=Path, required=True, help='Directory for all extracted artifacts')
    parser.add_argument(
        '--backend-order',
        nargs='+',
        default=['docling', 'marker', 'mineru', 'pdfimages'],
        choices=['docling', 'marker', 'mineru', 'pdfimages'],
        help='Backends to try, in order.',
    )
    parser.add_argument(
        '--mineru-backend',
        default='pipeline',
        help='MinerU backend to request. Use an empty string to let MinerU choose.',
    )
    parser.add_argument(
        '--render-pages',
        action='store_true',
        help='Also rasterize full PDF pages with pdftoppm as a last-resort visual fallback.',
    )
    parser.add_argument(
        '--probe-only',
        action='store_true',
        help='Only report available modules and commands, then exit.',
    )
    args = parser.parse_args()

    pdf_path = args.pdf.resolve()
    out_dir = ensure_dir(args.out_dir.resolve())

    if not pdf_path.exists():
        print(f'PDF not found: {pdf_path}', file=sys.stderr)
        return 2

    manifest: dict[str, Any] = {
        'pdf': str(pdf_path),
        'probe': probe_backends(),
        'backend_order': args.backend_order,
        'results': {},
    }

    if args.probe_only:
        write_json(out_dir / 'manifest.json', manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0

    for backend in args.backend_order:
        backend_dir = ensure_dir(out_dir / backend)
        if backend == 'docling':
            manifest['results'][backend] = export_docling(pdf_path, backend_dir)
        elif backend == 'marker':
            manifest['results'][backend] = export_marker(pdf_path, backend_dir)
        elif backend == 'mineru':
            manifest['results'][backend] = export_mineru(pdf_path, backend_dir, args.mineru_backend)
        elif backend == 'pdfimages':
            manifest['results'][backend] = export_pdfimages(pdf_path, backend_dir, args.render_pages)

    write_json(out_dir / 'manifest.json', manifest)
    payload = json.dumps(manifest, ensure_ascii=False, indent=2)
    try:
        print(payload)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(payload.encode('utf-8', errors='replace'))
        sys.stdout.buffer.write(b'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


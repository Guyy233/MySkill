from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import unicodedata
from pathlib import Path
from typing import Any

# Disable SSL revocation check — required when HuggingFace API calls go through
# an HTTP proxy that doesn't support CRL/OCSP checks (e.g. Clash on Windows).
os.environ.setdefault("HF_HUB_DISABLE_SSL_REVOCATION_CHECKS", "1")


def bootstrap_extra_site() -> None:
    extra = os.environ.get('PAPER_READING_HTML_EXTRA_SITE', '').strip()
    if not extra:
        return
    for raw in extra.split(os.pathsep):
        candidate = raw.strip()
        if candidate and candidate not in sys.path:
            sys.path.insert(0, candidate)


bootstrap_extra_site()


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_stem(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in normalized).strip("-").lower()
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    if cleaned:
        return cleaned
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()[:8]
    return f"paper-{digest}"


def export_docling(pdf_path: Path, out_dir: Path) -> dict[str, Any]:
    if not module_available("docling"):
        return {
            "status": "missing_dependency",
            "backend": "docling",
            "message": "Install docling first: pip install docling",
        }

    from docling.document_converter import DocumentConverter, InputFormat, PdfFormatOption  # type: ignore
    from docling.datamodel.pipeline_options import PdfPipelineOptions  # type: ignore
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend  # type: ignore

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.do_formula_enrichment = False  # requires network for CodeFormulaV2 model download
    pipeline_options.do_code_enrichment = False     # requires network for CodeFormulaV2 model download
    format_option = PdfFormatOption(
        pipeline_options=pipeline_options,
        backend=PyPdfiumDocumentBackend,
    )
    converter = DocumentConverter(format_options={InputFormat.PDF: format_option})
    result = converter.convert(str(pdf_path))
    document = result.document
    base_name = safe_stem(pdf_path.stem)

    outputs: dict[str, str] = {}

    exporters = {
        "markdown": ("export_to_markdown", ".md"),
        "html": ("export_to_html", ".html"),
        "doctags": ("export_to_doctags", ".doctags"),
    }

    for label, (method_name, suffix) in exporters.items():
        if hasattr(document, method_name):
            payload = getattr(document, method_name)()
            out_path = out_dir / f"{base_name}{suffix}"
            write_text(out_path, payload)
            outputs[label] = str(out_path)

    if hasattr(document, "export_to_dict"):
        json_payload: Any = document.export_to_dict()
    elif hasattr(document, "model_dump"):
        json_payload = document.model_dump()
    else:
        json_payload = {"document_type": type(document).__name__}

    json_path = out_dir / f"{base_name}.json"
    write_json(json_path, json_payload)
    outputs["json"] = str(json_path)

    return {
        "status": "ok",
        "backend": "docling",
        "source_name": pdf_path.name,
        "artifact_base_name": base_name,
        "outputs": outputs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a layout-aware first pass with Docling and write artifacts for paper-reading-html."
    )
    parser.add_argument("pdf", type=Path, help="Path to the source PDF")
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory where Docling artifacts should be written",
    )
    args = parser.parse_args()

    pdf_path = args.pdf.resolve()
    out_dir = ensure_dir(args.out_dir.resolve())

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return 2

    result = export_docling(pdf_path, out_dir)
    write_json(out_dir / "manifest.json", result)

    if result["status"] != "ok":
        print(result["message"])
        return 0

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    try:
        print(payload)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(payload.encode('utf-8', errors='replace'))
        sys.stdout.buffer.write(b'\n')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

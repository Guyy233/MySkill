from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from rapid_latex_ocr import LaTeXOCR


def main() -> int:
    parser = argparse.ArgumentParser(description='OCR formula images with RapidLaTeXOCR.')
    parser.add_argument('--input-dir', type=Path, required=True, help='Directory containing formula-*.png images')
    parser.add_argument('--out-json', type=Path, required=True, help='Output JSON path')
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    out_json = args.out_json.resolve()
    images = sorted(input_dir.glob('formula-*.png'))

    engine = LaTeXOCR()
    payload: dict[str, Any] = {}
    for image_path in images:
        try:
            image = Image.open(image_path).convert('RGB')
            result = engine(np.array(image))
            image.close()
            if isinstance(result, tuple):
                latex, elapsed = result
            else:
                latex, elapsed = str(result), None
            payload[image_path.name] = {
                'latex': latex,
                'elapsed': elapsed,
                'status': 'ok',
            }
        except Exception as exc:
            payload[image_path.name] = {
                'latex': '',
                'elapsed': None,
                'status': 'error',
                'error': str(exc),
            }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

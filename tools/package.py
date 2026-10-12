#!/usr/bin/env python3
"""Build a reproducible mod ZIP from mod/ into dist/.

Same inputs give byte-identical output: sorted entries, fixed timestamps and permissions.
"""
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD_DIR = ROOT / "mod"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def build(out_dir: Path = ROOT / "dist") -> Path:
    modinfo = json.loads((MOD_DIR / "modinfo.json").read_text(encoding="utf-8"))
    folder = f"[Gameplay] {modinfo['ModName']['English']}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{modinfo['ModID']}-{modinfo['Version']}.zip"
    files = sorted(p for p in MOD_DIR.rglob("*") if p.is_file() and p.name != ".DS_Store")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            info = zipfile.ZipInfo(f"{folder}/{path.relative_to(MOD_DIR).as_posix()}", FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
    return out


if __name__ == "__main__":
    print(build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist"))

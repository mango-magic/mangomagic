#!/usr/bin/env python3
"""Build a deterministic download from the reviewed public starter files."""
from pathlib import Path
import hashlib
import json
import stat
import zipfile
ROOT = Path(__file__).resolve().parents[1]
files = sorted(p for p in (ROOT / 'starter').rglob('*') if p.is_file())
manifest = {}
with zipfile.ZipFile(ROOT / 'assets/AI-Operations-Starter.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        if path.is_symlink():
            raise ValueError('No symlinks in starter package')
        relative = path.relative_to(ROOT / 'starter').as_posix()
        content = path.read_bytes()
        manifest[relative] = hashlib.sha256(content).hexdigest()
        info = zipfile.ZipInfo('AI Operations/' + relative, date_time=(2026, 9, 14, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = (stat.S_IFREG | 0o644) << 16
        archive.writestr(info, content)
(ROOT / 'assets/starter-manifest.json').write_text(json.dumps({'file_count': len(files), 'sha256': manifest}, indent=2) + '\n')
print(f'Packed {len(files)} starter files')

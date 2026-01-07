import os
import shutil
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / (ROOT.name + "-final-repo")
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

INCLUDE = [
    "src",
    "pyproject.toml",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "Dockerfile",
    "examples",
    "benchmarks",
]

for name in INCLUDE:
    p = ROOT / name
    if not p.exists():
        continue
    dest = OUT / name
    if p.is_dir():
        shutil.copytree(p, dest)
    else:
        shutil.copy2(p, dest)

# create zip
zip_path = OUT.with_suffix('.zip')
if zip_path.exists():
    zip_path.unlink()
shutil.make_archive(str(OUT), 'zip', root_dir=OUT)

# checksum
h = hashlib.sha256()
with open(zip_path, 'rb') as f:
    for chunk in iter(lambda: f.read(8192), b''):
        h.update(chunk)
print(str(zip_path))
print(h.hexdigest())

import os
import zipfile
import hashlib

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
zip_name = os.path.join(root, "llm-eval-final-submission.zip")
exclude_dirs = {'.venv', '.git', 'dist', 'build', '__pycache__', '.pytest_cache'}
exclude_files = {'llm-eval-final-submission.zip'}

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    for dirpath, dirnames, filenames in os.walk(root):
        # skip excluded directories
        rel_dir = os.path.relpath(dirpath, root)
        parts = rel_dir.split(os.sep)
        if parts[0] in exclude_dirs:
            continue
        for fn in filenames:
            if fn in exclude_files or fn.endswith('.pyc') or fn.endswith('.pyo'):
                continue
            file_path = os.path.join(dirpath, fn)
            arcname = os.path.join(rel_dir, fn) if rel_dir != '.' else fn
            zf.write(file_path, arcname)

# compute sha256
h = hashlib.sha256()
with open(zip_name, 'rb') as f:
    for chunk in iter(lambda: f.read(8192), b''):
        h.update(chunk)
print(zip_name)
print(h.hexdigest())

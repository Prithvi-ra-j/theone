# tools/generate_requirements_from_sitepackages.py
import glob, os, sys

venv_site = os.path.join("backend", ".venv311", "Lib", "site-packages")
if not os.path.isdir(venv_site):
    print("Site-packages not found at:", venv_site, file=sys.stderr)
    sys.exit(1)

reqs = []
for dist in glob.glob(os.path.join(venv_site, "*.dist-info")):
    meta = os.path.join(dist, "METADATA")
    if not os.path.isfile(meta):
        meta = os.path.join(dist, "PKG-INFO")
    if not os.path.isfile(meta):
        continue
    name = None
    version = None
    with open(meta, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("Name: "):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("Version: "):
                version = line.split(":", 1)[1].strip()
            if name and version:
                break
    if name and version:
        reqs.append(f"{name}=={version}")

reqs = sorted(set(reqs))
out_path = os.path.join("backend", "requirements_from_old_venv.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(reqs))
print("Wrote", out_path, "with", len(reqs), "packages")
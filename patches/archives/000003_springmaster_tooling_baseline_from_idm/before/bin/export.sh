#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_FILE="${APP_EXPORT_CONFIG_FILE:-${PROJECT_ROOT}/export.config.json}"

python3 - "${PROJECT_ROOT}" "${CONFIG_FILE}" "$@" <<'PYEXPORT'
from __future__ import annotations
import fnmatch, json, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1]).resolve()
config_file = Path(sys.argv[2]).resolve()
args = sys.argv[3:]

def fail(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def load_config():
    try:
        return json.loads(config_file.read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f"Cannot read export config {config_file}: {exc}", 2)

def as_list(v):
    if v is None: return []
    if isinstance(v, list): return [str(x) for x in v]
    if isinstance(v, str): return [x for x in v.split() if x]
    fail(f"Invalid list value in export config: {v!r}", 2)

def match_any(rel, patterns):
    return any(fnmatch.fnmatchcase(rel, pat) or fnmatch.fnmatchcase('/'+rel, pat) for pat in patterns)

def collect_files(cfg, profile):
    profiles = cfg.get('profiles') or {}
    if profile not in profiles:
        fail(f"Unknown export profile: {profile}", 2)
    spec = profiles[profile]
    includes = as_list(spec.get('include')) or ['**/*']
    excludes = as_list(spec.get('exclude')) + as_list(cfg.get('globalExclude'))
    negated = [p[1:] for p in excludes if p.startswith('!')]
    excludes = [p for p in excludes if not p.startswith('!')]
    result = []
    for p in sorted(root.rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        inc = match_any(rel, includes)
        exc = match_any(rel, excludes)
        unexc = match_any(rel, negated)
        if inc and (not exc or unexc):
            result.append(rel)
    return result

def write_export(cfg, profile, zip_output=False):
    generated = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    project = cfg.get('projectKey') or root.name
    output_dir = root / (cfg.get('outputDirectory') or 'exports/text')
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = generated.replace(':','-').replace('.','-').replace('Z','Z')
    out_dir = output_dir / f"{project}_export_{profile}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    files = collect_files(cfg, profile)
    txt = out_dir / f"{project}_export_{profile}.txt"
    with txt.open('w', encoding='utf-8') as fh:
        fh.write(f"# {project} Text Export\n\nGeneratedAt: {generated}\nRepositoryRoot: {root}\nProfiles: {profile}\nFiles: {len(files)}\n\n")
        fh.write('## Files\n')
        for rel in files:
            fh.write(f"- {rel}\n")
        for rel in files:
            fh.write("\n" + "="*80 + f"\nFILE: {rel}\n" + "="*80 + "\n")
            path = root / rel
            try:
                fh.write(path.read_text(encoding='utf-8'))
                fh.write('\n')
            except UnicodeDecodeError:
                fh.write('[binary file skipped]\n')
    meta = {
        'profiles': [profile],
        'exportMode': 'bootstrap-text',
        'generatedAt': generated,
        'repositoryRoot': str(root),
        'configFile': str(config_file.relative_to(root)) if root in config_file.parents or config_file == root else str(config_file),
        'outputFile': str(txt.relative_to(root)),
        'fileCount': len(files),
        'includedFiles': files,
    }
    meta_path = out_dir / f"{project}_export_{profile}.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if zip_output:
        zip_path = out_dir.with_suffix('.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out_dir.rglob('*')):
                z.write(p, p.relative_to(output_dir).as_posix())
        print(zip_path.relative_to(root))
    else:
        print(txt.relative_to(root))

cfg = load_config()
if not args or args[0] in ('help','--help','-h'):
    print('Usage: ./bin/export.sh [full|root|docs|patches|java|resources|tests|db|platform|core|demo|tooling] [--zip]')
    sys.exit(0)
profile = args[0]
zip_output = '--zip' in args
write_export(cfg, profile, zip_output=zip_output)
PYEXPORT

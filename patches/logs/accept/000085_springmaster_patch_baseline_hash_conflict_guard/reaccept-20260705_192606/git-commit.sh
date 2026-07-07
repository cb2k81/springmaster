#!/usr/bin/env bash
set -euo pipefail

cd '/opt/cocondo/springmaster'

echo "Git-Status vor Commit:"
git status --short

files=(
  '.gitignore'
  'PROJECT_DOCS/TOOLING/PATCH_ACCEPT_VERIFY_WORKFLOW.md'
  'PROJECT_DOCS/TOOLING/PATCH_SYSTEM.md'
  'PROJECT_DOCS/TOOLING/PATCH_VALIDATION_POLICY.md'
  'bin/patch-system-it.sh'
  'bin/patch.py'
  'export.config.json'
  'patches/logs/root/CHANGELOG-000085_springmaster_patch_baseline_hash_conflict_guard.md'
  'platform/versions/platform.env'
)

allowed_file="$(mktemp)"
trap 'rm -f "${allowed_file}"' EXIT
printf '%s\n' "${files[@]}" > "${allowed_file}"

unexpected_staged=()
while IFS= read -r staged_path; do
  [[ -z "${staged_path}" ]] && continue
  if ! grep -Fx -- "${staged_path}" "${allowed_file}" >/dev/null; then
    unexpected_staged+=("${staged_path}")
  fi
done < <(git diff --cached --name-only)

if (( ${#unexpected_staged[@]} > 0 )); then
  echo "GIT_INDEX_DIRTY: staged files outside this patch would be committed."
  printf '  %s\n' "${unexpected_staged[@]}"
  echo "Bitte fremde staged Änderungen committen oder unstagen und dieses Skript danach erneut ausführen."
  exit 23
fi

echo "Stage patchbezogene Dateien:"
printf '  %s\n' "${files[@]}"
git add -- "${files[@]}"

echo "Git-Status nach Staging:"
git status --short

git commit -m 'Apply 000085_springmaster_patch_baseline_hash_conflict_guard'

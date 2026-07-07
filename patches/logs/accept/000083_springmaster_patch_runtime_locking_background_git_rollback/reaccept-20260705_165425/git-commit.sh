#!/usr/bin/env bash
set -euo pipefail

cd '/opt/cocondo/springmaster'

echo "Git-Status vor Commit:"
git status --short

files=(
  '.env.example'
  'PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md'
  'PROJECT_DOCS/TOOLING/PATCH_ACCEPT_VERIFY_WORKFLOW.md'
  'PROJECT_DOCS/TOOLING/PATCH_SYSTEM.md'
  'PROJECT_DOCS/TOOLING/PATCH_VALIDATION_POLICY.md'
  'bin/patch-system-it.sh'
  'bin/patch.py'
  'patches/logs/root/CHANGELOG-000082_springmaster_patch_runtime_locking_background_git_rollback.md'
  'platform/versions/platform.env'
)

echo "Stage patchbezogene Dateien:"
printf '  %s\n' "${files[@]}"
git add -- "${files[@]}"

echo "Git-Status nach Staging:"
git status --short

git commit -m 'Apply 000083_springmaster_patch_runtime_locking_background_git_rollback'

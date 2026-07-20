#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/init.env.sh"

TARGET_DIR="${PLATFORM_UPDATE_TARGET_DIR:-${PROJECT_ROOT}/platform/update/targets}"
BUILD_WORKSPACE_DIR="${PLATFORM_UPDATE_BUILD_WORKSPACE_DIR:-${PROJECT_ROOT}/build/platform-update}"
MANIFEST_DIR="${BUILD_WORKSPACE_DIR}/manifests"
GENERATED_DIR="${BUILD_WORKSPACE_DIR}/generated"
LOG_DIR="${BUILD_WORKSPACE_DIR}/logs"
PAYLOAD_DIR="${BUILD_WORKSPACE_DIR}/payload"

print_usage() {
  cat <<'USAGE'
Usage:
  ./bin/platform-update.sh help
  ./bin/platform-update.sh list
  ./bin/platform-update.sh show <target>
  ./bin/platform-update.sh validate <target|all>
  ./bin/platform-update.sh plan <target> [--profile core|core-runtime|core-tests|core-docs|platform-update-doc|tooling|tooling-cutover|defaults|demo|platform-update] [--output <dir>]
  ./bin/platform-update.sh generate <target> [--profile core|core-runtime|core-tests|core-docs|platform-update-doc|tooling|tooling-cutover|defaults|demo|platform-update] [--output <dir>] [--dry-run]
  ./bin/platform-update.sh preflight <target> --zip <generated-patch.zip> [--output <dir>]
  ./bin/platform-update.sh compatibility-plan <target> --zip <generated-patch.zip> [--output <dir>] [--dry-run]
  ./bin/platform-update.sh apply-plan <target> --zip <generated-patch.zip> [--output <dir>] [--dry-run]
  ./bin/platform-update.sh target-apply <target> --zip <generated-patch.zip> [--output <dir>] [--dry-run]
  ./bin/platform-update.sh workspace

Commands:
  list       list configured target descriptors
  show       print one target descriptor
  validate   validate descriptor syntax and report local target availability
  plan       create a non-invasive update plan file; no target project is modified
  generate   create a target-local plan patch ZIP; no target project is modified
  preflight  run the target-local patch system in dry-run mode for a generated patch ZIP
  compatibility-plan create a target compatibility patch ZIP and review plan; no target project is modified
  apply-plan create a review-gated target apply plan; no target project is modified
  target-apply explicitly apply a generated patch in the target project with compact logging
  workspace  print the current platform-update build workspace paths

Default generated artifacts are written below build/platform-update/**.
The generate command resets this workspace before writing a new default output set.
Payload profiles are intentionally split. Profile core includes runtime + tests, but not master Core documentation. Use core-docs explicitly for PROJECT_DOCS/CORE/**. Profile defaults is reserved for baseline configuration defaults such as .env.example and export.config.json and must be reviewed explicitly because these files are target-local.

Safety model:
  generate, preflight, compatibility-plan and apply-plan do not modify target projects.
  apply-plan is a review gate and intentionally does not emit an executable target-mutating script.
  target-apply is the only platform-update command that may modify a target project.
  target-apply writes full target output to build/platform-update/logs/** and prints only a compact status summary.
USAGE
}

fail_update() {
  echo "[ERROR] $*" >&2
  exit 1
}

warn_update() {
  echo "[WARN] $*" >&2
}

ensure_build_workspace() {
  mkdir -p "${GENERATED_DIR}" "${MANIFEST_DIR}" "${LOG_DIR}" "${PAYLOAD_DIR}"
}

reset_build_workspace() {
  rm -rf "${BUILD_WORKSPACE_DIR}"
  ensure_build_workspace
}

using_default_generated_output() {
  [[ "${UPDATE_OUTPUT_DIR:-}" == "${GENERATED_DIR}" ]]
}

print_workspace() {
  cat <<WORKSPACE_EOF
BUILD_WORKSPACE_DIR=${BUILD_WORKSPACE_DIR}
GENERATED_DIR=${GENERATED_DIR}
MANIFEST_DIR=${MANIFEST_DIR}
LOG_DIR=${LOG_DIR}
PAYLOAD_DIR=${PAYLOAD_DIR}
WORKSPACE_EOF
}

safe_target_name() {
  local value="$1"
  [[ "${value}" =~ ^[A-Za-z0-9._-]+$ ]] || fail_update "Invalid target name: ${value}"
  printf '%s' "${value}"
}

safe_profile_name() {
  local value="$1"
  case "${value}" in
    core|core-runtime|core-tests|core-docs|platform-update-doc|tooling|tooling-cutover|defaults|demo|platform-update) printf '%s' "${value}" ;;
    *) fail_update "Unsupported update profile: ${value}" ;;
  esac
}

sanitize_token() {
  printf '%s' "$1" | sed -E 's/[^A-Za-z0-9._-]+/-/g; s/^-+//; s/-+$//'
}

count_files_under() {
  local dir="$1"
  if [[ -d "${dir}" ]]; then
    find "${dir}" -type f | wc -l | tr -d ' '
  else
    echo "0"
  fi
}

copy_tree_payload() {
  local source_rel="$1"
  local target_root="$2"
  local source_abs="${PROJECT_ROOT}/${source_rel}"
  [[ -e "${source_abs}" ]] || return 0

  if [[ -d "${source_abs}" ]]; then
    mkdir -p "${target_root}/${source_rel}"
    cp -a "${source_abs}/." "${target_root}/${source_rel}/"
  elif [[ -f "${source_abs}" ]]; then
    mkdir -p "${target_root}/$(dirname "${source_rel}")"
    cp -a "${source_abs}" "${target_root}/${source_rel}"
  fi
}

core_runtime_payload_paths() {
  cat <<'PAYLOAD_EOF'
src/main/java/de/cocondo/system
PAYLOAD_EOF
}

core_tests_payload_paths() {
  cat <<'PAYLOAD_EOF'
src/test/java/de/cocondo/system
PAYLOAD_EOF
}

core_docs_payload_paths() {
  cat <<'PAYLOAD_EOF'
PROJECT_DOCS/CORE
PAYLOAD_EOF
}

tooling_payload_paths() {
  cat <<'PAYLOAD_EOF'
bin/patch.py
bin/patch.sh
bin/export.sh
bin/init.env.sh
bin/tooling-selfcheck.sh
bin/dbtool.sh
bin/patch-artifact-preflight.py
bin/patch-artifact-preflight-it.sh
bin/export-integrity-check.py
bin/export-integrity-it.sh
bin/lib
PROJECT_DOCS/TOOLING
PAYLOAD_EOF
}

defaults_payload_paths() {
  cat <<'PAYLOAD_EOF'
.env.example
export.config.json
PROJECT_DOCS/CONFIG/SPRINGMASTER_ENV_TEMPLATE.env
PAYLOAD_EOF
}

collect_payload_paths_for_profile() {
  local profile="$1"
  case "${profile}" in
    core)
      core_runtime_payload_paths
      core_tests_payload_paths
      ;;
    core-runtime)
      core_runtime_payload_paths
      ;;
    core-tests)
      core_tests_payload_paths
      ;;
    core-docs)
      core_docs_payload_paths
      ;;
    tooling|tooling-cutover)
      tooling_payload_paths
      ;;
    defaults)
      defaults_payload_paths
      ;;
    platform-update-doc)
      return 0
      ;;
    *)
      return 0
      ;;
  esac
}

generated_scope_for_profile() {
  local profile="$1"
  case "${profile}" in
    core|core-runtime|core-tests) echo "core" ;;
    core-docs|platform-update-doc) echo "docs" ;;
    tooling|tooling-cutover) echo "tooling" ;;
    defaults) echo "root" ;;
    demo) echo "demo" ;;
    platform-update) echo "platform-update" ;;
    *) echo "root" ;;
  esac
}

profile_generates_payload() {
  local profile="$1"
  case "${profile}" in
    core|core-runtime|core-tests|core-docs|tooling|tooling-cutover|defaults|platform-update-doc) return 0 ;;
    *) return 1 ;;
  esac
}

profile_payload_summary() {
  local profile="$1"
  case "${profile}" in
    core) echo "core runtime + core tests; no master Core documentation" ;;
    core-runtime) echo "core runtime only" ;;
    core-tests) echo "core tests only" ;;
    core-docs) echo "master Core documentation only" ;;
    platform-update-doc) echo "generated platform-update document only" ;;
    tooling) echo "shared tooling payload without target-local defaults" ;;
    tooling-cutover) echo "shared tooling payload plus target-safe synthesized export configuration" ;;
    defaults) echo "baseline configuration defaults (.env.example, export.config.json, env template)" ;;
    demo|platform-update) echo "profile reserved for later dedicated payload rules" ;;
    *) echo "unknown" ;;
  esac
}

profile_payload_listing() {
  local profile="$1"
  local listing
  listing="$(collect_payload_paths_for_profile "${profile}" | sed '/^$/d' || true)"
  if [[ -z "${listing}" ]]; then
    echo "(generated scope-local PROJECT_DOCS/<scope>/PLATFORM_UPDATES/<update-id>.md only)"
  else
    printf '%s\n' "${listing}"
  fi
  if [[ "${profile}" == "tooling-cutover" ]]; then
    echo "export.config.json (target-safe synthesized bootstrap configuration)"
  fi
}

generated_doc_rel_for_profile() {
  local profile="$1"
  local patch_id="$2"
  case "${profile}" in
    core|core-runtime|core-tests|core-docs)
      echo "PROJECT_DOCS/CORE/PLATFORM_UPDATES/${patch_id}.md"
      ;;
    tooling|tooling-cutover)
      echo "PROJECT_DOCS/TOOLING/PLATFORM_UPDATES/${patch_id}.md"
      ;;
    platform-update-doc|platform-update)
      echo "PROJECT_DOCS/TOOLING/PLATFORM_UPDATE_${patch_id}.md"
      ;;
    defaults|*)
      echo "PROJECT_DOCS/PLATFORM_UPDATES/${patch_id}.md"
      ;;
  esac
}

profile_requires_target_pom_core_dependencies() {
  local profile="$1"
  case "${profile}" in
    core|core-runtime) return 0 ;;
    *) return 1 ;;
  esac
}

write_core_ready_target_pom() {
  local target_pom="$1"
  local output_pom="$2"
  [[ -f "${target_pom}" ]] || fail_update "Target pom.xml not found for Core dependency synthesis: ${target_pom}"
  mkdir -p "$(dirname "${output_pom}")"
  python3 - "${target_pom}" "${output_pom}" <<'POM_PY'
import pathlib
import re
import sys

source = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
text = source.read_text()

required = [
    ("jakarta.persistence", "jakarta.persistence-api"),
    ("jakarta.validation", "jakarta.validation-api"),
    ("org.springframework.data", "spring-data-commons"),
]

def has_dependency(content: str, group_id: str, artifact_id: str) -> bool:
    pattern = (
        r"<dependency>\s*"
        r"(?:(?!</dependency>).)*?<groupId>" + re.escape(group_id) + r"</groupId>"
        r"(?:(?!</dependency>).)*?<artifactId>" + re.escape(artifact_id) + r"</artifactId>"
        r"(?:(?!</dependency>).)*?</dependency>"
    )
    return re.search(pattern, content, flags=re.DOTALL) is not None

def dependency_xml(group_id: str, artifact_id: str) -> str:
    return (
        "        <dependency>\n"
        f"            <groupId>{group_id}</groupId>\n"
        f"            <artifactId>{artifact_id}</artifactId>\n"
        "        </dependency>"
    )

missing = [dep for dep in required if not has_dependency(text, *dep)]
if missing:
    insertion = "\n" + "\n".join(dependency_xml(*dep) for dep in missing) + "\n"
    marker = "    </dependencies>"
    if marker not in text:
        raise SystemExit("pom.xml does not contain </dependencies>; cannot add Core dependencies")
    text = text.replace(marker, insertion + marker, 1)

target.write_text(text)
POM_PY
}

count_profile_payload_files() {
  local profile="$1"
  local rel total source_abs
  total=0
  while IFS= read -r rel; do
    [[ -n "${rel}" ]] || continue
    source_abs="${PROJECT_ROOT}/${rel}"
    if [[ -d "${source_abs}" ]]; then
      total=$((total + $(count_files_under "${source_abs}")))
    elif [[ -f "${source_abs}" ]]; then
      total=$((total + 1))
    fi
  done < <(collect_payload_paths_for_profile "${profile}")
  if [[ "${profile}" == "tooling-cutover" ]]; then
    total=$((total + 1))
  fi
  echo "${total}"
}

target_file() {
  local target
  target="$(safe_target_name "$1")"
  printf '%s/%s.env' "${TARGET_DIR}" "${target}"
}

resolve_update_path() {
  local value="$1"
  if [[ "${value}" = /* ]]; then
    printf '%s' "${value}"
  else
    printf '%s/%s' "${PROJECT_ROOT}" "${value}"
  fi
}

read_patch_manifest_field() {
  local zip_path="$1"
  local field="$2"
  python3 - "${zip_path}" "${field}" <<'PY_FIELD'
import json
import sys
import zipfile

zip_path = sys.argv[1]
field = sys.argv[2]
with zipfile.ZipFile(zip_path) as zf:
    with zf.open("manifest.json") as fh:
        manifest = json.load(fh)
value = manifest
for part in field.split("."):
    if not isinstance(value, dict):
        value = ""
        break
    value = value.get(part, "")
if isinstance(value, (dict, list)):
    print(json.dumps(value, ensure_ascii=False))
else:
    print(value)
PY_FIELD
}

validate_generated_patch_binding() {
  local zip_path="$1"
  local required_target required_profile
  required_target="$(read_patch_manifest_field "${zip_path}" "requires.target")"
  required_profile="$(read_patch_manifest_field "${zip_path}" "requires.profile")"
  if [[ -n "${required_target}" && "${required_target}" != "${TARGET_NAME}" ]]; then
    fail_update "Generated patch target mismatch: manifest=${required_target}, command=${TARGET_NAME}."
  fi
  if [[ -n "${required_profile}" ]]; then
    require_profile_allowed_for_loaded_target "${required_profile}"
  fi
}

accept_validation_profile_for_generated_profile() {
  local generated_profile="$1"
  case "${generated_profile}" in
    tooling|tooling-cutover)
      echo "tooling"
      ;;
    core|core-runtime|core-tests)
      echo "code"
      ;;
    core-docs|platform-update-doc)
      echo "docs"
      ;;
    defaults|platform-update)
      echo "tooling"
      ;;
    *)
      fail_update "No target accept validation profile is defined for generated profile: ${generated_profile}"
      ;;
  esac
}

generated_profile_requires_full_test() {
  local generated_profile="$1"
  case "${generated_profile}" in
    tooling|tooling-cutover|core|core-runtime|core-tests|defaults|platform-update)
      return 0
      ;;
    core-docs|platform-update-doc)
      return 1
      ;;
    *)
      fail_update "No full-test policy is defined for generated profile: ${generated_profile}"
      ;;
  esac
}

accept_summary_value() {
  local summary_file="$1"
  local key="$2"
  sed -n "s/^${key}=//p" "${summary_file}" | tail -n 1
}


load_platform_versions() {
  # shellcheck source=/dev/null
  source "${PROJECT_ROOT}/platform/versions/platform.env"
}

load_target() {
  local file="$1"
  [[ -f "${file}" ]] || fail_update "Target descriptor not found: ${file}"

  unset TARGET_NAME TARGET_STATUS TARGET_PATH TARGET_APP_NAME TARGET_BASE_PACKAGE TARGET_PORT TARGET_DB_NAME TARGET_STAGE_DB_NAME TARGET_LIFECYCLE TARGET_INITIALIZATION_ALLOWED TARGET_UPDATE_ALLOWED TARGET_DELIVERY_ENABLED TARGET_ALLOWED_PROFILES TARGET_NOTES

  local key value
  while IFS='=' read -r key value || [[ -n "${key:-}" ]]; do
    [[ -n "${key:-}" ]] || continue
    [[ "${key}" != \#* ]] || continue
    case "${key}" in
      TARGET_NAME) TARGET_NAME="${value:-}" ;;
      TARGET_STATUS) TARGET_STATUS="${value:-}" ;;
      TARGET_PATH) TARGET_PATH="${value:-}" ;;
      TARGET_APP_NAME) TARGET_APP_NAME="${value:-}" ;;
      TARGET_BASE_PACKAGE) TARGET_BASE_PACKAGE="${value:-}" ;;
      TARGET_PORT) TARGET_PORT="${value:-}" ;;
      TARGET_DB_NAME) TARGET_DB_NAME="${value:-}" ;;
      TARGET_STAGE_DB_NAME) TARGET_STAGE_DB_NAME="${value:-}" ;;
      TARGET_LIFECYCLE) TARGET_LIFECYCLE="${value:-}" ;;
      TARGET_INITIALIZATION_ALLOWED) TARGET_INITIALIZATION_ALLOWED="${value:-}" ;;
      TARGET_UPDATE_ALLOWED) TARGET_UPDATE_ALLOWED="${value:-}" ;;
      TARGET_DELIVERY_ENABLED) TARGET_DELIVERY_ENABLED="${value:-}" ;;
      TARGET_ALLOWED_PROFILES) TARGET_ALLOWED_PROFILES="${value:-}" ;;
      TARGET_NOTES) TARGET_NOTES="${value:-}" ;;
      *) ;;
    esac
  done < "${file}"

  [[ -n "${TARGET_NAME:-}" ]] || fail_update "TARGET_NAME missing in ${file}"
  [[ -n "${TARGET_STATUS:-}" ]] || fail_update "TARGET_STATUS missing in ${file}"
  [[ -n "${TARGET_PATH:-}" ]] || fail_update "TARGET_PATH missing in ${file}"
  [[ "${TARGET_NAME}" =~ ^[A-Za-z0-9._-]+$ ]] || fail_update "TARGET_NAME contains unsupported characters in ${file}: ${TARGET_NAME}"
  [[ "${TARGET_PATH}" = /* ]] || fail_update "TARGET_PATH must be absolute in ${file}: ${TARGET_PATH}"
}

list_targets() {
  [[ -d "${TARGET_DIR}" ]] || fail_update "Target directory missing: ${TARGET_DIR}"
  printf '%-16s %-34s %s\n' "TARGET" "STATUS" "PATH"
  local file
  while IFS= read -r file; do
    load_target "${file}"
    printf '%-16s %-34s %s\n' "${TARGET_NAME}" "${TARGET_STATUS}" "${TARGET_PATH}"
  done < <(find "${TARGET_DIR}" -maxdepth 1 -type f -name '*.env' | sort)
}

show_target() {
  local file
  file="$(target_file "$1")"
  load_target "${file}"
  cat <<TARGET_EOF
TARGET_NAME=${TARGET_NAME}
TARGET_STATUS=${TARGET_STATUS}
TARGET_PATH=${TARGET_PATH}
TARGET_APP_NAME=${TARGET_APP_NAME:-}
TARGET_BASE_PACKAGE=${TARGET_BASE_PACKAGE:-}
TARGET_PORT=${TARGET_PORT:-}
TARGET_DB_NAME=${TARGET_DB_NAME:-}
TARGET_STAGE_DB_NAME=${TARGET_STAGE_DB_NAME:-}
TARGET_LIFECYCLE=${TARGET_LIFECYCLE:-}
TARGET_INITIALIZATION_ALLOWED=${TARGET_INITIALIZATION_ALLOWED:-}
TARGET_UPDATE_ALLOWED=${TARGET_UPDATE_ALLOWED:-}
TARGET_DELIVERY_ENABLED=${TARGET_DELIVERY_ENABLED:-false}
TARGET_ALLOWED_PROFILES=${TARGET_ALLOWED_PROFILES:-}
TARGET_NOTES=${TARGET_NOTES:-}
TARGET_EOF
}

validate_loaded_target() {
  local result="OK"
  if [[ "${TARGET_STATUS}" != VERIFIED* ]]; then
    warn_update "${TARGET_NAME}: status is ${TARGET_STATUS}; descriptor is not verified for automatic updates."
  fi
  if [[ -d "${TARGET_PATH}" ]]; then
    if [[ -x "${TARGET_PATH}/bin/patch.sh" ]]; then
      echo "[OK] ${TARGET_NAME}: target path exists and local patch system is executable."
    elif [[ -f "${TARGET_PATH}/bin/patch.sh" ]]; then
      warn_update "${TARGET_NAME}: ${TARGET_PATH}/bin/patch.sh exists but is not executable."
      result="WARN"
    else
      warn_update "${TARGET_NAME}: target path exists but bin/patch.sh is missing."
      result="WARN"
    fi
  else
    warn_update "${TARGET_NAME}: target path does not exist locally: ${TARGET_PATH}"
    result="WARN"
  fi
  echo "[${result}] ${TARGET_NAME}: descriptor syntax valid."
}

target_delivery_enabled() {
  [[ "${TARGET_DELIVERY_ENABLED:-false}" == "true" ]]
}

profile_allowed_for_loaded_target() {
  local requested="$1"
  local token
  while IFS= read -r token; do
    [[ -n "${token}" ]] || continue
    [[ "${token}" == "${requested}" ]] && return 0
  done < <(printf '%s\n' "${TARGET_ALLOWED_PROFILES:-}" | tr ',;' '\n' | tr ' ' '\n' | sed '/^$/d')
  return 1
}

require_profile_allowed_for_loaded_target() {
  local requested="$1"
  profile_allowed_for_loaded_target "${requested}" || fail_update     "${TARGET_NAME}: profile ${requested} is not allowed by TARGET_ALLOWED_PROFILES=${TARGET_ALLOWED_PROFILES:-}."
}

require_clean_target_git() {
  [[ -d "${TARGET_PATH}/.git" || -f "${TARGET_PATH}/.git" ]] ||     fail_update "${TARGET_NAME}: target path is not a Git worktree: ${TARGET_PATH}"
  local status
  status="$(git -C "${TARGET_PATH}" status --porcelain --untracked-files=all)" ||     fail_update "${TARGET_NAME}: cannot read target Git status."
  [[ -z "${status}" ]] || fail_update     "${TARGET_NAME}: target Git working tree is not clean; generated baseline hashes would be unsafe."
}

latest_target_patch_id() {
  local latest=""
  if [[ -x "${TARGET_PATH}/bin/patch.sh" ]]; then
    latest="$(cd "${TARGET_PATH}" && ./bin/patch.sh show latest 2>/dev/null | sed -n 's/^Patch-ID:[[:space:]]*//p' | head -n 1 || true)"
  fi
  if [[ -z "${latest}" && -d "${TARGET_PATH}/patches/archives" ]]; then
    latest="$(find "${TARGET_PATH}/patches/archives" -maxdepth 1 -type f -name '[0-9][0-9][0-9][0-9][0-9][0-9]_*.zip' -printf '%f\n' 2>/dev/null | sed 's/\.zip$//' | sort | tail -n 1 || true)"
  fi
  printf '%s' "${latest}"
}

next_target_patch_number() {
  local latest digits number
  latest="$(latest_target_patch_id)"
  if [[ "${latest}" =~ ^([0-9]{6})_ ]]; then
    digits="${BASH_REMATCH[1]}"
    number=$((10#${digits} + 1))
  else
    number=1
  fi
  printf '%06d' "${number}"
}

run_producer_artifact_preflight() {
  local zip_path="$1"
  local output_dir="$2"
  [[ -f "${PROJECT_ROOT}/bin/patch-artifact-preflight.py" ]] || \
    fail_update "Producer artifact preflight is missing: ${PROJECT_ROOT}/bin/patch-artifact-preflight.py"
  rm -rf "${output_dir}"
  python3 "${PROJECT_ROOT}/bin/patch-artifact-preflight.py" \
    "${TARGET_PATH}" "${zip_path}" --output "${output_dir}" --no-export \
    --engine "${PROJECT_ROOT}/bin/patch.py"
}


require_target_delivery_enabled_for_apply() {
  if target_delivery_enabled; then
    return 0
  fi
  fail_update "${TARGET_NAME}: target delivery is disabled by descriptor (TARGET_DELIVERY_ENABLED=${TARGET_DELIVERY_ENABLED:-false}). Initialize or reclassify the target explicitly before target-apply."
}

validate_targets() {
  local subject="$1"
  if [[ "${subject}" == "all" ]]; then
    local file
    while IFS= read -r file; do
      load_target "${file}"
      validate_loaded_target
    done < <(find "${TARGET_DIR}" -maxdepth 1 -type f -name '*.env' | sort)
  else
    local file
    file="$(target_file "${subject}")"
    load_target "${file}"
    validate_loaded_target
  fi
}

parse_profile_output_args() {
  local mode="$1"
  shift
  UPDATE_TARGET=""
  UPDATE_PROFILE="core"
  UPDATE_OUTPUT_DIR="${MANIFEST_DIR}"
  UPDATE_DRY_RUN="false"

  if [[ "${mode}" == "generate" ]]; then
    UPDATE_OUTPUT_DIR="${GENERATED_DIR}"
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --profile)
        [[ $# -ge 2 ]] || fail_update "--profile requires a value"
        UPDATE_PROFILE="$(safe_profile_name "$2")"
        shift 2
        ;;
      --output|--output-dir)
        [[ $# -ge 2 ]] || fail_update "$1 requires a value"
        UPDATE_OUTPUT_DIR="$2"
        shift 2
        ;;
      --dry-run)
        UPDATE_DRY_RUN="true"
        shift
        ;;
      -* )
        fail_update "Unknown ${mode} option: $1"
        ;;
      *)
        [[ -z "${UPDATE_TARGET}" ]] || fail_update "${mode} expects exactly one target"
        UPDATE_TARGET="$1"
        shift
        ;;
    esac
  done

  [[ -n "${UPDATE_TARGET}" ]] || fail_update "${mode} expects a target"
  UPDATE_TARGET="$(safe_target_name "${UPDATE_TARGET}")"
}

create_plan() {
  parse_profile_output_args "plan" "$@"
  local file timestamp plan_path
  file="$(target_file "${UPDATE_TARGET}")"
  load_target "${file}"
  load_platform_versions
  ensure_build_workspace
  mkdir -p "${UPDATE_OUTPUT_DIR}"
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  plan_path="${UPDATE_OUTPUT_DIR}/${timestamp}_${TARGET_NAME}_${UPDATE_PROFILE}_plan.env"

  cat > "${plan_path}" <<PLAN_EOF
UPDATE_PLAN_ID=${timestamp}_${TARGET_NAME}_${UPDATE_PROFILE}
UPDATE_PLAN_CREATED_AT=${timestamp}
UPDATE_PLAN_STATUS=PLANNED_ONLY
UPDATE_PLAN_PROFILE=${UPDATE_PROFILE}
TARGET_NAME=${TARGET_NAME}
TARGET_STATUS=${TARGET_STATUS}
TARGET_PATH=${TARGET_PATH}
TARGET_LIFECYCLE=${TARGET_LIFECYCLE:-}
TARGET_INITIALIZATION_ALLOWED=${TARGET_INITIALIZATION_ALLOWED:-}
TARGET_UPDATE_ALLOWED=${TARGET_UPDATE_ALLOWED:-}
TARGET_DELIVERY_ENABLED=${TARGET_DELIVERY_ENABLED:-false}
TARGET_ALLOWED_PROFILES=${TARGET_ALLOWED_PROFILES:-}
MASTER_PLATFORM_VERSION=${PLATFORM_VERSION:-}
MASTER_CORE_VERSION=${PLATFORM_CORE_VERSION:-}
MASTER_TOOLING_VERSION=${PLATFORM_TOOLING_VERSION:-}
MASTER_DEMO_VERSION=${PLATFORM_DEMO_VERSION:-}
MASTER_PLATFORM_UPDATE_VERSION=${PLATFORM_UPDATE_VERSION:-}
NEXT_STEP=Generate a target-local patch ZIP with platform-update generate.
PLAN_EOF

  echo "Platform-Update-Plan:"
  echo "  Status:       PLANNED_ONLY"
  echo "  Target:       ${TARGET_NAME}"
  echo "  Profile:      ${UPDATE_PROFILE}"
  echo "  Plan:         ${plan_path}"
  echo "  Target path:  ${TARGET_PATH}"
}

create_target_plan_patch() {
  parse_profile_output_args "generate" "$@"
  local file safe_profile target_patch_name target_patch_id target_artifact_id zip_path tmp_dir doc_rel changelog_rel generated_scope payload_file_count payload_status payload_summary payload_listing
  local finalizer_summary producer_preflight_dir target_latest
  file="$(target_file "${UPDATE_TARGET}")"
  load_target "${file}"
  load_platform_versions

  require_profile_allowed_for_loaded_target "${UPDATE_PROFILE}"
  [[ "${TARGET_UPDATE_ALLOWED:-false}" == "true" ]] || \
    fail_update "${TARGET_NAME}: target updates are disabled by descriptor."
  require_clean_target_git

  safe_profile="$(sanitize_token "${UPDATE_PROFILE}")"
  target_patch_name="springmaster_platform_update_${safe_profile}_for_${TARGET_NAME}"
  target_patch_id="$(next_target_patch_number)_${target_patch_name}"
  target_artifact_id="$(python3 -c 'import uuid; print(f"urn:uuid:{uuid.uuid4()}")')"
  zip_path="${UPDATE_OUTPUT_DIR}/${target_patch_id}.zip"
  doc_rel="$(generated_doc_rel_for_profile "${UPDATE_PROFILE}" "${target_patch_id}")"
  changelog_rel="logs/CHANGELOG-${target_patch_id}.md"
  generated_scope="$(generated_scope_for_profile "${UPDATE_PROFILE}")"
  payload_status="plan-only"
  payload_file_count="$(count_profile_payload_files "${UPDATE_PROFILE}")"
  payload_summary="$(profile_payload_summary "${UPDATE_PROFILE}")"
  payload_listing="$(profile_payload_listing "${UPDATE_PROFILE}")"
  target_latest="$(latest_target_patch_id)"

  if profile_generates_payload "${UPDATE_PROFILE}"; then
    payload_status="payload"
  fi

  if [[ "${UPDATE_DRY_RUN}" == "true" ]]; then
    echo "Platform-Update-Generate:"
    echo "  Status:       DRY-RUN"
    echo "  Target:       ${TARGET_NAME}"
    echo "  Profile:      ${UPDATE_PROFILE}"
    echo "  Scope:        ${generated_scope}"
    echo "  Artifact-ID:  ${target_artifact_id}"
    echo "  Patch-ID:     ${target_patch_id}"
    echo "  Previous:     ${target_latest:-<none>}"
    echo "  ZIP:          ${zip_path}"
    echo "  Payload:      ${payload_status}"
    echo "  Payload-Files:${payload_file_count}"
    echo "  Target path:  ${TARGET_PATH}"
    echo "  Hinweis:      Zielprojekt wird nicht verändert."
    return 0
  fi

  if using_default_generated_output; then
    reset_build_workspace
  else
    ensure_build_workspace
    mkdir -p "${UPDATE_OUTPUT_DIR}"
  fi
  mkdir -p "${PROJECT_ROOT}/tmp"
  tmp_dir="$(mktemp -d "${PROJECT_ROOT}/tmp/platform-update-generate.XXXXXX")"
  trap '[[ -n "${tmp_dir:-}" ]] && rm -rf "${tmp_dir}"' RETURN

  mkdir -p "${tmp_dir}/files/$(dirname "${doc_rel}")" "${tmp_dir}/logs"

  local rel
  while IFS= read -r rel; do
    [[ -n "${rel}" ]] || continue
    copy_tree_payload "${rel}" "${tmp_dir}/files"
  done < <(collect_payload_paths_for_profile "${UPDATE_PROFILE}")

  if [[ "${UPDATE_PROFILE}" == "tooling-cutover" ]]; then
    python3 "${PROJECT_ROOT}/platform/update/tools/synthesize-tooling-cutover-config.py" \
      --target-root "${TARGET_PATH}" \
      --output-root "${tmp_dir}/files" \
      --target-name "${TARGET_NAME}" >/dev/null
  fi

  if profile_requires_target_pom_core_dependencies "${UPDATE_PROFILE}"; then
    write_core_ready_target_pom "${TARGET_PATH}/pom.xml" "${tmp_dir}/files/pom.xml"
  fi

  cat > "${tmp_dir}/files/${doc_rel}" <<DOC_EOF
# Springmaster Platform Update

## Status

This target-bound patch was generated by Springmaster \`platform-update generate\`.
Generation and producer preflight are non-mutating for the target repository.

## Target

| Field | Value |
|---|---|
| Target | ${TARGET_NAME} |
| Status | ${TARGET_STATUS} |
| Path | ${TARGET_PATH} |
| App | ${TARGET_APP_NAME:-} |
| Base Package | ${TARGET_BASE_PACKAGE:-} |
| Lifecycle | ${TARGET_LIFECYCLE:-} |
| Update Allowed | ${TARGET_UPDATE_ALLOWED:-} |
| Delivery Enabled | ${TARGET_DELIVERY_ENABLED:-false} |
| Allowed Profiles | ${TARGET_ALLOWED_PROFILES:-} |
| Profile | ${UPDATE_PROFILE} |
| Generated Scope | ${generated_scope} |
| Artifact ID | ${target_artifact_id} |
| Patch ID | ${target_patch_id} |
| Previous Target Patch | ${target_latest:-none} |
| Payload Mode | ${payload_status} |
| Source Payload Files | ${payload_file_count} |

## Master Versions

| Version | Value |
|---|---|
| PLATFORM_VERSION | ${PLATFORM_VERSION:-} |
| PLATFORM_CORE_VERSION | ${PLATFORM_CORE_VERSION:-} |
| PLATFORM_TOOLING_VERSION | ${PLATFORM_TOOLING_VERSION:-} |
| PLATFORM_TEMPLATE_VERSION | ${PLATFORM_TEMPLATE_VERSION:-} |
| PLATFORM_DEMO_VERSION | ${PLATFORM_DEMO_VERSION:-} |
| PLATFORM_UPDATE_VERSION | ${PLATFORM_UPDATE_VERSION:-} |
| PLATFORM_STATE_PATCH | ${PLATFORM_STATE_PATCH:-} |

## Payload

Selected payload profile: \`${UPDATE_PROFILE}\`

Payload summary: ${payload_summary}

The generated patch contains only files whose bytes or executable mode differ from the current target baseline. Every effective operation has a target-bound \`expectedBeforeSha256\` entry.

Source payload paths:

\`\`\`text
${payload_listing}
\`\`\`

## Qualification

The generator performs the Springmaster producer artifact preflight against an isolated Git worktree of the clean target baseline. No target file is changed during generation or preflight.

## Application

After review, the real target application remains explicit:

\`\`\`bash
./bin/platform-update.sh target-apply ${TARGET_NAME} --zip build/platform-update/generated/${target_patch_id}.zip
\`\`\`
DOC_EOF

  cat > "${tmp_dir}/${changelog_rel}" <<CHANGELOG_EOF
# ${target_patch_id}

Generated by Springmaster \`platform-update generate\`.

* Target: ${TARGET_NAME}
* Artifact ID: ${target_artifact_id}
* Previous target patch: ${target_latest:-none}
* Profile: ${UPDATE_PROFILE}
* Generated scope: ${generated_scope}
* Payload mode: ${payload_status}
* Source payload files: ${payload_file_count}
* Master platform version: ${PLATFORM_VERSION:-}
* Master core version: ${PLATFORM_CORE_VERSION:-}
* Master tooling version: ${PLATFORM_TOOLING_VERSION:-}
* Master platform-update version: ${PLATFORM_UPDATE_VERSION:-}

The target repository was not modified during generation or producer artifact preflight.
CHANGELOG_EOF

  finalizer_summary="$(python3 "${PROJECT_ROOT}/platform/update/tools/finalize-target-patch.py" \
    --root "${tmp_dir}" \
    --target-root "${TARGET_PATH}" \
    --patch-id "${target_patch_id}" \
    --artifact-id "${target_artifact_id}" \
    --name "${target_patch_name}" \
    --scope "${generated_scope}" \
    --target-name "${TARGET_NAME}" \
    --profile "${UPDATE_PROFILE}" \
    --master-platform-version "${PLATFORM_VERSION:-}" \
    --master-core-version "${PLATFORM_CORE_VERSION:-}" \
    --master-tooling-version "${PLATFORM_TOOLING_VERSION:-}" \
    --master-platform-update-version "${PLATFORM_UPDATE_VERSION:-}")"

  python3 - "${tmp_dir}" "${zip_path}" <<'ZIP_PY'
import pathlib
import sys
import zipfile

root = pathlib.Path(sys.argv[1])
zip_path = pathlib.Path(sys.argv[2])
zip_path.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            zf.write(path, path.relative_to(root).as_posix())
ZIP_PY

  producer_preflight_dir="${MANIFEST_DIR}/${target_patch_id}_producer_preflight"
  run_producer_artifact_preflight "${zip_path}" "${producer_preflight_dir}" >/dev/null

  echo "Platform-Update-Generate:"
  echo "  Status:       GENERATED_AND_PREFLIGHTED"
  echo "  Target:       ${TARGET_NAME}"
  echo "  Profile:      ${UPDATE_PROFILE}"
  echo "  Scope:        ${generated_scope}"
  echo "  Artifact-ID:  ${target_artifact_id}"
  echo "  Patch-ID:     ${target_patch_id}"
  echo "  Previous:     ${target_latest:-<none>}"
  echo "  Source-Files: ${payload_file_count}"
  echo "  Operations:   $(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["operationCount"])' "${finalizer_summary}")"
  echo "  ZIP:          ${zip_path}"
  echo "  ZIP-SHA256:   $(sha256sum "${zip_path}" | awk '{print $1}')"
  echo "  Preflight:    ${producer_preflight_dir}/REPORT.json"
  echo "  Target path:  ${TARGET_PATH}"
  echo "  Hinweis:      Zielprojekt wurde nicht verändert."
}


parse_preflight_args() {
  UPDATE_TARGET=""
  UPDATE_PATCH_ZIP=""
  UPDATE_OUTPUT_DIR="${MANIFEST_DIR}"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --zip|--patch|--patch-zip)
        [[ $# -ge 2 ]] || fail_update "$1 requires a value"
        UPDATE_PATCH_ZIP="$(resolve_update_path "$2")"
        shift 2
        ;;
      --output|--output-dir)
        [[ $# -ge 2 ]] || fail_update "$1 requires a value"
        UPDATE_OUTPUT_DIR="$2"
        shift 2
        ;;
      -* )
        fail_update "Unknown preflight option: $1"
        ;;
      *)
        [[ -z "${UPDATE_TARGET}" ]] || fail_update "preflight expects exactly one target"
        UPDATE_TARGET="$1"
        shift
        ;;
    esac
  done

  [[ -n "${UPDATE_TARGET}" ]] || fail_update "preflight expects a target"
  [[ -n "${UPDATE_PATCH_ZIP}" ]] || fail_update "preflight requires --zip <generated-patch.zip>"
  UPDATE_TARGET="$(safe_target_name "${UPDATE_TARGET}")"
  [[ -f "${UPDATE_PATCH_ZIP}" ]] || fail_update "Generated patch ZIP not found: ${UPDATE_PATCH_ZIP}"
}

run_target_patch_preflight() {
  local timestamp patch_id_for_log
  patch_id_for_log="$(sanitize_token "${patch_id:-unknown-patch}")"
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  PREFLIGHT_LOG="${UPDATE_OUTPUT_DIR}/${timestamp}_${TARGET_NAME}_${patch_id_for_log}_preflight.log"
  PREFLIGHT_STATUS="FAILED"
  PREFLIGHT_DETAIL=""

  mkdir -p "${UPDATE_OUTPUT_DIR}"

  if [[ ! -d "${TARGET_PATH}" ]]; then
    PREFLIGHT_DETAIL="Target path does not exist: ${TARGET_PATH}"
    printf '%s\n' "${PREFLIGHT_DETAIL}" > "${PREFLIGHT_LOG}"
    return 1
  fi

  if [[ ! -f "${TARGET_PATH}/bin/patch.sh" ]]; then
    PREFLIGHT_DETAIL="Target patch system is missing: ${TARGET_PATH}/bin/patch.sh"
    printf '%s\n' "${PREFLIGHT_DETAIL}" > "${PREFLIGHT_LOG}"
    return 1
  fi

  if [[ ! -x "${TARGET_PATH}/bin/patch.sh" ]]; then
    PREFLIGHT_DETAIL="Target patch system is not executable: ${TARGET_PATH}/bin/patch.sh"
    printf '%s\n' "${PREFLIGHT_DETAIL}" > "${PREFLIGHT_LOG}"
    return 1
  fi

  if (cd "${TARGET_PATH}" && ./bin/patch.sh apply --dry-run "${UPDATE_PATCH_ZIP}") > "${PREFLIGHT_LOG}" 2>&1; then
    PREFLIGHT_STATUS="PASSED"
    PREFLIGHT_DETAIL="Target dry-run succeeded."
    return 0
  fi

  PREFLIGHT_DETAIL="Target dry-run failed. See preflight log."
  return 1
}

create_preflight() {
  parse_preflight_args "$@"
  local file
  file="$(target_file "${UPDATE_TARGET}")"
  load_target "${file}"
  load_platform_versions
  validate_generated_patch_binding "${UPDATE_PATCH_ZIP}"
  require_clean_target_git

  patch_id="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "patchId")"
  patch_artifact_id="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "artifactId")"
  patch_name="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "name")"
  patch_scope="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "scope")"
  [[ -n "${patch_id}" ]] || fail_update "manifest.id missing in ${UPDATE_PATCH_ZIP}"
  [[ -n "${patch_scope}" ]] || fail_update "manifest.scope missing in ${UPDATE_PATCH_ZIP}"

  if run_target_patch_preflight; then
    echo "Platform-Update-Preflight:"
    echo "  Status:       PASSED"
    echo "  Target:       ${TARGET_NAME}"
    echo "  Artifact-ID:  ${patch_artifact_id}"
    echo "  Patch-ID:     ${patch_id}"
    echo "  Patch-Scope:  ${patch_scope}"
    echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
    echo "  Log:          ${PREFLIGHT_LOG}"
    echo "  Hinweis:      Zielprojekt wurde nicht verändert."
    return 0
  fi

  echo "Platform-Update-Preflight:"
  echo "  Status:       FAILED"
  echo "  Target:       ${TARGET_NAME}"
  echo "  Artifact-ID:  ${patch_artifact_id}"
  echo "  Patch-ID:     ${patch_id}"
  echo "  Patch-Scope:  ${patch_scope}"
  echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
  echo "  Log:          ${PREFLIGHT_LOG}"
  echo "  Grund:        ${PREFLIGHT_DETAIL}"
  echo "  Hinweis:      Zielprojekt wurde nicht verändert."
  return 1
}

parse_apply_plan_args() {
  UPDATE_TARGET=""
  UPDATE_PATCH_ZIP=""
  UPDATE_OUTPUT_DIR="${MANIFEST_DIR}"
  UPDATE_DRY_RUN="false"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --zip|--patch|--patch-zip)
        [[ $# -ge 2 ]] || fail_update "$1 requires a value"
        UPDATE_PATCH_ZIP="$(resolve_update_path "$2")"
        shift 2
        ;;
      --output|--output-dir)
        [[ $# -ge 2 ]] || fail_update "$1 requires a value"
        UPDATE_OUTPUT_DIR="$2"
        shift 2
        ;;
      --dry-run)
        UPDATE_DRY_RUN="true"
        shift
        ;;
      -* )
        fail_update "Unknown apply-plan option: $1"
        ;;
      *)
        [[ -z "${UPDATE_TARGET}" ]] || fail_update "apply-plan expects exactly one target"
        UPDATE_TARGET="$1"
        shift
        ;;
    esac
  done

  [[ -n "${UPDATE_TARGET}" ]] || fail_update "apply-plan expects a target"
  [[ -n "${UPDATE_PATCH_ZIP}" ]] || fail_update "apply-plan requires --zip <generated-patch.zip>"
  UPDATE_TARGET="$(safe_target_name "${UPDATE_TARGET}")"
  [[ -f "${UPDATE_PATCH_ZIP}" ]] || fail_update "Generated patch ZIP not found: ${UPDATE_PATCH_ZIP}"
}


parse_compatibility_plan_args() {
  UPDATE_TARGET=""
  UPDATE_PATCH_ZIP=""
  UPDATE_OUTPUT_DIR="${MANIFEST_DIR}"
  UPDATE_DRY_RUN="false"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --zip|--patch|--patch-zip)
        [[ $# -ge 2 ]] || fail_update "$1 requires a value"
        UPDATE_PATCH_ZIP="$(resolve_update_path "$2")"
        shift 2
        ;;
      --output|--output-dir)
        [[ $# -ge 2 ]] || fail_update "$1 requires a value"
        UPDATE_OUTPUT_DIR="$2"
        shift 2
        ;;
      --dry-run)
        UPDATE_DRY_RUN="true"
        shift
        ;;
      -* )
        fail_update "Unknown compatibility-plan option: $1"
        ;;
      *)
        [[ -z "${UPDATE_TARGET}" ]] || fail_update "compatibility-plan expects exactly one target"
        UPDATE_TARGET="$1"
        shift
        ;;
    esac
  done

  [[ -n "${UPDATE_TARGET}" ]] || fail_update "compatibility-plan expects a target"
  [[ -n "${UPDATE_PATCH_ZIP}" ]] || fail_update "compatibility-plan requires --zip <generated-patch.zip>"
  UPDATE_TARGET="$(safe_target_name "${UPDATE_TARGET}")"
  [[ -f "${UPDATE_PATCH_ZIP}" ]] || fail_update "Generated patch ZIP not found: ${UPDATE_PATCH_ZIP}"
}

create_target_compatibility_patch_zip() {
  local target_patch_id="$1"
  local target_patch_name="$2"
  local requested_scope="$3"
  local zip_path="$4"
  local tmp_dir doc_rel changelog_rel manifest_path target_artifact_id

  target_artifact_id="$(python3 -c 'import uuid; print(f"urn:uuid:{uuid.uuid4()}")')"

  tmp_dir="$(mktemp -d)"
  doc_rel="$(generated_doc_rel_for_profile "${UPDATE_PROFILE}" "${target_patch_id}")"
  changelog_rel="logs/CHANGELOG-${target_patch_id}.md"
  manifest_path="${tmp_dir}/manifest.json"

  mkdir -p "${tmp_dir}/files/bin"
  cp "${PROJECT_ROOT}/bin/patch.py" "${tmp_dir}/files/bin/patch.py"
  cp "${PROJECT_ROOT}/bin/patch.sh" "${tmp_dir}/files/bin/patch.sh"

  mkdir -p "${tmp_dir}/files/PROJECT_DOCS/PLATFORM_UPDATES" "${tmp_dir}/logs"

  cat > "${tmp_dir}/files/${doc_rel}" <<DOC_EOF
# Target Patchsystem Compatibility Update

This patch was generated by Springmaster \`platform-update compatibility-plan\`.

## Purpose

The target project could not dry-run the generated Springmaster update patch.
The requested patch scope was:

\`\`\`text
${requested_scope}
\`\`\`

The generated compatibility patch updates only the target-local patch entrypoint and patch engine:

\`\`\`text
bin/patch.sh
bin/patch.py
\`\`\`

The goal is to make the target patch system understand the current Springmaster patch format, including standard scopes such as \`core\` and project-local scope extensions from \`.env\`.

## Project-local scopes

Project-specific additional scopes and paths must remain local to the target project. They belong in the target project's \`.env\`, for example:

\`\`\`env
PATCH_LOCAL_SCOPES=reporting
PATCH_SCOPE_REPORTING_PATHS=src/main/java/com/example/reporting/**;src/test/java/com/example/reporting/**
PATCH_SCOPE_REPORTING_LOG_DIR=reporting
\`\`\`

This compatibility patch does not hard-code target-specific paths in Springmaster.
DOC_EOF

  cat > "${tmp_dir}/${changelog_rel}" <<CHANGELOG_EOF
# ${target_patch_id}

Generated by Springmaster \`platform-update compatibility-plan\`.

* Target: ${TARGET_NAME}
* Requested generated patch scope: ${requested_scope}
* Updates target-local patchsystem entrypoint and engine.
* Does not add target-specific paths to Springmaster.
* Project-specific additional scopes must be configured in the target project's \`.env\`.
CHANGELOG_EOF

  cat > "${manifest_path}" <<MANIFEST_EOF
{
  "schemaVersion": "springmaster.patch-manifest.v2",
  "artifactId": "${target_artifact_id}",
  "id": "${target_patch_id}",
  "patchId": "${target_patch_id}",
  "name": "${target_patch_name}",
  "scope": "root",
  "description": "Generated Springmaster compatibility patch for target ${TARGET_NAME}; updates target-local patch tooling before applying ${requested_scope} updates.",
  "type": "platform-update-compatibility",
  "requires": {
    "target": "${TARGET_NAME}",
    "requestedPatchScope": "${requested_scope}",
    "masterPlatformVersion": "${PLATFORM_VERSION:-}",
    "masterPlatformUpdateVersion": "${PLATFORM_UPDATE_VERSION:-}"
  },
  "changes": [
    "Updates bin/patch.py to the current Springmaster patch engine",
    "Updates bin/patch.sh to the current Springmaster patch entrypoint",
    "Documents project-local scope extension via .env"
  ]
}
MANIFEST_EOF

  python3 - "${tmp_dir}" "${zip_path}" <<'ZIP_PY'
import pathlib
import sys
import zipfile

root = pathlib.Path(sys.argv[1])
zip_path = pathlib.Path(sys.argv[2])
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            zf.write(path, path.relative_to(root).as_posix())
ZIP_PY

  rm -rf "${tmp_dir}"
}

create_compatibility_plan() {
  parse_compatibility_plan_args "$@"
  local file timestamp patch_id patch_name patch_scope compatibility_id compatibility_name compatibility_zip plan_base plan_md plan_env target_zip_rel target_zip_path preflight_status_for_plan
  file="$(target_file "${UPDATE_TARGET}")"
  load_target "${file}"
  load_platform_versions

  patch_id="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "id")"
  patch_name="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "name")"
  patch_scope="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "scope")"
  [[ -n "${patch_id}" ]] || fail_update "manifest.id missing in ${UPDATE_PATCH_ZIP}"
  [[ -n "${patch_scope}" ]] || fail_update "manifest.scope missing in ${UPDATE_PATCH_ZIP}"

  ensure_build_workspace
  mkdir -p "${UPDATE_OUTPUT_DIR}" "${GENERATED_DIR}"
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  compatibility_id="${timestamp}_springmaster_platform_update_compatibility_for_${TARGET_NAME}"
  compatibility_name="springmaster_platform_update_compatibility_for_${TARGET_NAME}"
  compatibility_zip="${GENERATED_DIR}/${compatibility_id}.zip"
  plan_base="${timestamp}_${TARGET_NAME}_${patch_id}_compatibility_plan"
  plan_md="${UPDATE_OUTPUT_DIR}/${plan_base}.md"
  plan_env="${UPDATE_OUTPUT_DIR}/${plan_base}.env"
  target_zip_rel="tmp/platform-updates/${compatibility_id}.zip"
  target_zip_path="${TARGET_PATH}/${target_zip_rel}"

  if run_target_patch_preflight; then
    preflight_status_for_plan="PASSED"
  else
    preflight_status_for_plan="FAILED"
  fi

  if [[ "${UPDATE_DRY_RUN}" == "true" ]]; then
    echo "Platform-Update-Compatibility-Plan:"
    echo "  Status:             DRY-RUN"
    echo "  Target:             ${TARGET_NAME}"
    echo "  Patch-ID:           ${patch_id}"
    echo "  Patch-Scope:        ${patch_scope}"
    echo "  Source ZIP:         ${UPDATE_PATCH_ZIP}"
    echo "  Preflight:          ${PREFLIGHT_LOG}"
    echo "  Preflight-Status:   ${preflight_status_for_plan}"
    echo "  Compatibility ZIP:  ${compatibility_zip}"
    echo "  Plan:               ${plan_md}"
    echo "  Review Env:         ${plan_env}"
    echo "  Hinweis:            Zielprojekt wird nicht verändert. Realer Apply nur mit target-apply."
    return 0
  fi

  create_target_compatibility_patch_zip "${compatibility_id}" "${compatibility_name}" "${patch_scope}" "${compatibility_zip}"

  cat > "${plan_md}" <<PLAN_MD_EOF
# Springmaster Target Compatibility Review Plan

## Status

This compatibility plan was generated by Springmaster \`platform-update compatibility-plan\`.

Springmaster did not modify the target project. This plan is a review gate. It intentionally does not create an executable target-mutating apply script.

## Trigger

The generated target patch could not be accepted by the target patch system during preflight.

| Field | Value |
|---|---|
| Target | ${TARGET_NAME} |
| Target Path | ${TARGET_PATH} |
| Original Patch ID | ${patch_id} |
| Original Patch Scope | ${patch_scope} |
| Original ZIP | ${UPDATE_PATCH_ZIP} |
| Preflight Log | ${PREFLIGHT_LOG} |
| Preflight Status | ${preflight_status_for_plan} |

## Compatibility Patch

| Field | Value |
|---|---|
| Compatibility Patch ID | ${compatibility_id} |
| Compatibility ZIP | ${compatibility_zip} |
| Target ZIP | ${target_zip_path} |
| Compatibility Scope | root |

## Why this is needed

If the target preflight reports an unknown scope such as \`core\`, the target-local patch system is older than the generated Springmaster update patch expects.

The compatibility patch updates the target-local patch engine before the original generated update patch is retried.

## Project-local scope rule

Project-specific additional scopes and paths must be configured in the target project's \`.env\`. They must not be hard-coded centrally in Springmaster.

## Review gate

After review, the real target change is explicit and log-based:

\`\`\`bash
cd ${PROJECT_ROOT}
./bin/platform-update.sh target-apply ${TARGET_NAME} --zip ${compatibility_zip}
\`\`\`

After successful compatibility application, rerun:

\`\`\`bash
cd ${PROJECT_ROOT}
./bin/platform-update.sh preflight ${TARGET_NAME} --zip ${UPDATE_PATCH_ZIP}
./bin/platform-update.sh apply-plan ${TARGET_NAME} --zip ${UPDATE_PATCH_ZIP}
\`\`\`
PLAN_MD_EOF

  cat > "${plan_env}" <<PLAN_ENV_EOF
PLAN_TYPE=compatibility-plan
PLAN_STATUS=REVIEW_REQUIRED
TARGET_NAME=${TARGET_NAME}
TARGET_PATH=${TARGET_PATH}
SOURCE_PATCH_ID=${patch_id}
SOURCE_PATCH_SCOPE=${patch_scope}
SOURCE_PATCH_ZIP=${UPDATE_PATCH_ZIP}
PREFLIGHT_LOG=${PREFLIGHT_LOG}
PREFLIGHT_STATUS=${preflight_status_for_plan}
COMPATIBILITY_PATCH_ID=${compatibility_id}
COMPATIBILITY_ZIP=${compatibility_zip}
TARGET_ZIP=${target_zip_path}
NEXT_COMMAND=./bin/platform-update.sh target-apply ${TARGET_NAME} --zip ${compatibility_zip}
PLAN_ENV_EOF

  echo "Platform-Update-Compatibility-Plan:"
  echo "  Status:             REVIEW_REQUIRED"
  echo "  Target:             ${TARGET_NAME}"
  echo "  Patch-ID:           ${patch_id}"
  echo "  Patch-Scope:        ${patch_scope}"
  echo "  Source ZIP:         ${UPDATE_PATCH_ZIP}"
  echo "  Preflight:          ${PREFLIGHT_LOG}"
  echo "  Preflight-Status:   ${preflight_status_for_plan}"
  echo "  Compatibility ZIP:  ${compatibility_zip}"
  echo "  Plan:               ${plan_md}"
  echo "  Review Env:         ${plan_env}"
  echo "  Hinweis:            Zielprojekt wurde nicht verändert. Realer Apply nur mit target-apply."
}

create_apply_plan() {
  parse_apply_plan_args "$@"
  local file timestamp patch_id patch_name patch_scope zip_name plan_base plan_md plan_env target_zip_rel target_zip_path
  file="$(target_file "${UPDATE_TARGET}")"
  load_target "${file}"
  load_platform_versions

  patch_id="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "id")"
  patch_name="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "name")"
  patch_scope="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "scope")"
  [[ -n "${patch_id}" ]] || fail_update "manifest.id missing in ${UPDATE_PATCH_ZIP}"
  [[ -n "${patch_scope}" ]] || fail_update "manifest.scope missing in ${UPDATE_PATCH_ZIP}"

  if ! run_target_patch_preflight; then
    echo "Platform-Update-Apply-Plan:"
    echo "  Status:       PREFLIGHT_FAILED"
    echo "  Target:       ${TARGET_NAME}"
    echo "  Patch-ID:     ${patch_id}"
    echo "  Patch-Scope:  ${patch_scope}"
    echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
    echo "  Preflight:    ${PREFLIGHT_LOG}"
    echo "  Grund:        ${PREFLIGHT_DETAIL}"
    echo "  Hinweis:      Zielprojekt wurde nicht verändert. Kein Review-Gate erzeugt."
    return 1
  fi

  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  zip_name="$(basename "${UPDATE_PATCH_ZIP}")"
  plan_base="${timestamp}_${TARGET_NAME}_${patch_id}_apply_plan"
  plan_md="${UPDATE_OUTPUT_DIR}/${plan_base}.md"
  plan_env="${UPDATE_OUTPUT_DIR}/${plan_base}.env"
  target_zip_rel="tmp/platform-updates/${zip_name}"
  target_zip_path="${TARGET_PATH}/${target_zip_rel}"

  if [[ "${UPDATE_DRY_RUN}" == "true" ]]; then
    echo "Platform-Update-Apply-Plan:"
    echo "  Status:       DRY-RUN"
    echo "  Target:       ${TARGET_NAME}"
    echo "  Patch-ID:     ${patch_id}"
    echo "  Patch-Scope:  ${patch_scope}"
    echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
    echo "  Preflight:    ${PREFLIGHT_LOG}"
    echo "  Plan:         ${plan_md}"
    echo "  Review Env:   ${plan_env}"
    echo "  Target ZIP:   ${target_zip_path}"
    echo "  Hinweis:      Zielprojekt wird nicht verändert. Realer Apply nur mit target-apply."
    return 0
  fi

  ensure_build_workspace
  mkdir -p "${UPDATE_OUTPUT_DIR}"

  cat > "${plan_md}" <<PLAN_MD_EOF
# Springmaster Target Patch Review Gate

## Status

This apply plan was generated by Springmaster \`platform-update apply-plan\`.

Springmaster did not modify the target project. This file is a mandatory review gate. It intentionally does not create an executable target-mutating apply script.

## Target

| Field | Value |
|---|---|
| Target | ${TARGET_NAME} |
| Status | ${TARGET_STATUS} |
| Path | ${TARGET_PATH} |
| App | ${TARGET_APP_NAME:-} |
| Lifecycle | ${TARGET_LIFECYCLE:-} |
| Delivery Enabled | ${TARGET_DELIVERY_ENABLED:-false} |
| Allowed Profiles | ${TARGET_ALLOWED_PROFILES:-} |

## Patch

| Field | Value |
|---|---|
| Patch ID | ${patch_id} |
| Patch Name | ${patch_name} |
| Patch Scope | ${patch_scope} |
| Source ZIP | ${UPDATE_PATCH_ZIP} |
| Target ZIP | ${target_zip_path} |
| Preflight Log | ${PREFLIGHT_LOG} |
| Preflight Status | ${PREFLIGHT_STATUS} |

## Master Versions

| Version | Value |
|---|---|
| PLATFORM_VERSION | ${PLATFORM_VERSION:-} |
| PLATFORM_UPDATE_VERSION | ${PLATFORM_UPDATE_VERSION:-} |
| PLATFORM_STATE_PATCH | ${PLATFORM_STATE_PATCH:-} |

## Review decision

Before applying to the target project, review:

1. The generated patch ZIP content.
2. The target-local preflight log.
3. The patch scope and target path.
4. Whether the target project is allowed to be changed in this maintenance window.
5. Whether `TARGET_DELIVERY_ENABLED=true` is set for this target.
6. Whether target validation/export is required after application.

## Explicit target application

After review, the real target change is a separate explicit command:

\`\`\`bash
cd ${PROJECT_ROOT}
./bin/platform-update.sh target-apply ${TARGET_NAME} --zip ${UPDATE_PATCH_ZIP}
\`\`\`

The command copies the generated patch ZIP to the target project's \`tmp/platform-updates/**\` directory, invokes the target-local patch system through \`patch.sh accept\`, and stores the complete output under \`build/platform-update/logs/**\`.
PLAN_MD_EOF

  cat > "${plan_env}" <<PLAN_ENV_EOF
PLAN_TYPE=apply-plan
PLAN_STATUS=REVIEW_REQUIRED
TARGET_NAME=${TARGET_NAME}
TARGET_PATH=${TARGET_PATH}
PATCH_ID=${patch_id}
PATCH_NAME=${patch_name}
PATCH_SCOPE=${patch_scope}
SOURCE_ZIP=${UPDATE_PATCH_ZIP}
TARGET_ZIP=${target_zip_path}
PREFLIGHT_LOG=${PREFLIGHT_LOG}
PREFLIGHT_STATUS=${PREFLIGHT_STATUS}
TARGET_DELIVERY_ENABLED=${TARGET_DELIVERY_ENABLED:-false}
NEXT_COMMAND=./bin/platform-update.sh target-apply ${TARGET_NAME} --zip ${UPDATE_PATCH_ZIP}
PLAN_ENV_EOF

  echo "Platform-Update-Apply-Plan:"
  echo "  Status:       REVIEW_REQUIRED"
  echo "  Target:       ${TARGET_NAME}"
  echo "  Patch-ID:     ${patch_id}"
  echo "  Patch-Scope:  ${patch_scope}"
  echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
  echo "  Preflight:    ${PREFLIGHT_LOG}"
  echo "  Plan:         ${plan_md}"
  echo "  Review Env:   ${plan_env}"
  echo "  Target ZIP:   ${target_zip_path}"
  echo "  Hinweis:      Zielprojekt wurde nicht verändert. Realer Apply nur mit target-apply."
}

parse_target_apply_args() {
  UPDATE_TARGET=""
  UPDATE_PATCH_ZIP=""
  UPDATE_OUTPUT_DIR="${LOG_DIR}"
  UPDATE_DRY_RUN="false"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --zip|--patch|--patch-zip)
        [[ $# -ge 2 ]] || fail_update "$1 requires a value"
        UPDATE_PATCH_ZIP="$(resolve_update_path "$2")"
        shift 2
        ;;
      --output|--output-dir)
        [[ $# -ge 2 ]] || fail_update "$1 requires a value"
        UPDATE_OUTPUT_DIR="$2"
        shift 2
        ;;
      --dry-run)
        UPDATE_DRY_RUN="true"
        shift
        ;;
      -* )
        fail_update "Unknown target-apply option: $1"
        ;;
      *)
        [[ -z "${UPDATE_TARGET}" ]] || fail_update "target-apply expects exactly one target"
        UPDATE_TARGET="$1"
        shift
        ;;
    esac
  done

  [[ -n "${UPDATE_TARGET}" ]] || fail_update "target-apply expects a target"
  [[ -n "${UPDATE_PATCH_ZIP}" ]] || fail_update "target-apply requires --zip <generated-patch.zip>"
  UPDATE_TARGET="$(safe_target_name "${UPDATE_TARGET}")"
  [[ -f "${UPDATE_PATCH_ZIP}" ]] || fail_update "Generated patch ZIP not found: ${UPDATE_PATCH_ZIP}"
}

create_target_apply() {
  parse_target_apply_args "$@"
  local file timestamp patch_id patch_name patch_scope zip_name patch_id_for_log target_zip_rel target_zip_path apply_log summary_file target_export
  local producer_preflight_dir accept_log_dir accept_summary latest_export generated_profile accept_profile expected_full_test
  local accept_status accept_profile_result accept_full_test_result accept_export_result latest_export_result
  local evidence_file export_log integrity_log source_target_git_head target_export_rel export_before export_after new_export_count
  local -a accept_args
  file="$(target_file "${UPDATE_TARGET}")"
  load_target "${file}"
  load_platform_versions
  validate_generated_patch_binding "${UPDATE_PATCH_ZIP}"
  require_clean_target_git

  patch_id="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "id")"
  patch_name="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "name")"
  patch_scope="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "scope")"
  generated_profile="$(read_patch_manifest_field "${UPDATE_PATCH_ZIP}" "requires.profile")"
  [[ -n "${patch_id}" ]] || fail_update "manifest.id missing in ${UPDATE_PATCH_ZIP}"
  [[ -n "${patch_scope}" ]] || fail_update "manifest.scope missing in ${UPDATE_PATCH_ZIP}"
  [[ -n "${generated_profile}" ]] || fail_update "manifest.requires.profile missing in ${UPDATE_PATCH_ZIP}"

  accept_profile="$(accept_validation_profile_for_generated_profile "${generated_profile}")"
  accept_args=(--profile "${accept_profile}" --no-export)
  if generated_profile_requires_full_test "${generated_profile}"; then
    expected_full_test="True"
    accept_args+=(--full-test)
  else
    expected_full_test="False"
    accept_args+=(--no-full-test)
  fi

  ensure_build_workspace
  mkdir -p "${UPDATE_OUTPUT_DIR}"
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  zip_name="$(basename "${UPDATE_PATCH_ZIP}")"
  patch_id_for_log="$(sanitize_token "${patch_id}")"
  target_zip_rel="tmp/platform-updates/${zip_name}"
  target_zip_path="${TARGET_PATH}/${target_zip_rel}"
  apply_log="${UPDATE_OUTPUT_DIR}/${timestamp}_${TARGET_NAME}_${patch_id_for_log}_target_apply.log"
  summary_file="${UPDATE_OUTPUT_DIR}/${timestamp}_${TARGET_NAME}_${patch_id_for_log}_target_apply.summary"
  producer_preflight_dir="${UPDATE_OUTPUT_DIR}/${timestamp}_${TARGET_NAME}_${patch_id_for_log}_producer_preflight"
  accept_log_dir="${TARGET_PATH}/patches/logs/validation/platform-update-${patch_id}"
  accept_summary="${accept_log_dir}/SUMMARY.txt"
  evidence_file="${TARGET_PATH}/tmp/platform-updates/${patch_id}_EXPORT_EVIDENCE.json"
  export_log="${UPDATE_OUTPUT_DIR}/${timestamp}_${TARGET_NAME}_${patch_id_for_log}_target_export.log"
  integrity_log="${UPDATE_OUTPUT_DIR}/${timestamp}_${TARGET_NAME}_${patch_id_for_log}_target_export_integrity.log"
  source_target_git_head="$(git -C "${TARGET_PATH}" rev-parse HEAD)"

  if ! run_producer_artifact_preflight "${UPDATE_PATCH_ZIP}" "${producer_preflight_dir}" >"${apply_log}.producer-preflight" 2>&1; then
    echo "Platform-Update-Target-Apply:"
    echo "  Status:       PRODUCER_PREFLIGHT_FAILED"
    echo "  Target:       ${TARGET_NAME}"
    echo "  Patch-ID:     ${patch_id}"
    echo "  Patch-Scope:  ${patch_scope}"
    echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
    echo "  Preflight:    ${producer_preflight_dir}/REPORT.json"
    echo "  Log:          ${apply_log}.producer-preflight"
    echo "  Export-Pfad:  "
    echo "  Hinweis:      Zielprojekt wurde nicht verändert."
    return 1
  fi

  if ! run_target_patch_preflight; then
    echo "Platform-Update-Target-Apply:"
    echo "  Status:       TARGET_DRY_RUN_FAILED"
    echo "  Target:       ${TARGET_NAME}"
    echo "  Patch-ID:     ${patch_id}"
    echo "  Patch-Scope:  ${patch_scope}"
    echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
    echo "  Preflight:    ${PREFLIGHT_LOG}"
    echo "  Log:          ${PREFLIGHT_LOG}"
    echo "  Export-Pfad:  "
    echo "  Hinweis:      Zielprojekt wurde nicht verändert."
    return 1
  fi

  if [[ "${UPDATE_DRY_RUN}" == "true" ]]; then
    echo "Platform-Update-Target-Apply:"
    echo "  Status:       DRY-RUN"
    echo "  Target:       ${TARGET_NAME}"
    echo "  Patch-ID:     ${patch_id}"
    echo "  Patch-Scope:  ${patch_scope}"
    echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
    echo "  Target ZIP:   ${target_zip_path}"
    echo "  Delivery:     ${TARGET_DELIVERY_ENABLED:-false}"
    echo "  Producer:     ${producer_preflight_dir}/REPORT.json"
    echo "  Target-Dry:   ${PREFLIGHT_LOG}"
    echo "  Validation:   profile=${accept_profile}, full-test=${expected_full_test}"
    echo "  Export-Pfad:  "
    echo "  Hinweis:      Zielprojekt wurde nicht verändert."
    return 0
  fi

  require_target_delivery_enabled_for_apply
  [[ ! -e "${accept_log_dir}" ]] || fail_update \
    "Target accept log directory already exists; refusing ambiguous reapply: ${accept_log_dir}"

  if (
    set -euo pipefail
    echo "== Springmaster target-apply =="
    echo "TARGET=${TARGET_NAME}"
    echo "TARGET_PATH=${TARGET_PATH}"
    echo "PATCH_ID=${patch_id}"
    echo "PATCH_SCOPE=${patch_scope}"
    echo "SOURCE_ZIP=${UPDATE_PATCH_ZIP}"
    echo "TARGET_ZIP=${target_zip_path}"
    echo "PRODUCER_PREFLIGHT=${producer_preflight_dir}/REPORT.json"
    echo "TARGET_DRY_RUN=${PREFLIGHT_LOG}"
    echo "GENERATED_PROFILE=${generated_profile}"
    echo "ACCEPT_PROFILE=${accept_profile}"
    echo "EXPECTED_FULL_TEST=${expected_full_test}"
    echo
    mkdir -p "$(dirname "${target_zip_path}")"
    cp "${UPDATE_PATCH_ZIP}" "${target_zip_path}"
    cd "${TARGET_PATH}"
    export APP_EXPORT_PROJECT_KEY="${TARGET_APP_NAME:-${TARGET_NAME}}"
    export APP_NAME="${TARGET_APP_NAME:-${TARGET_NAME}}"
    if [[ -n "${TARGET_BASE_PACKAGE:-}" ]]; then
      export APP_BASE_PACKAGE="${TARGET_BASE_PACKAGE}"
    fi
    PATCH_ACCEPT_LOG_DIR="${accept_log_dir}" ./bin/patch.sh accept "${target_zip_rel}" "${accept_args[@]}"
    echo
    echo "== Latest patch =="
    ./bin/patch.sh show latest
    [[ -f "${accept_summary}" ]] || {
      echo "Missing target accept summary: ${accept_summary}" >&2
      exit 1
    }
    accept_status="$(accept_summary_value "${accept_summary}" "STATUS")"
    accept_profile_result="$(accept_summary_value "${accept_summary}" "PROFILE")"
    accept_full_test_result="$(accept_summary_value "${accept_summary}" "FULL_TEST")"
    accept_export_result="$(accept_summary_value "${accept_summary}" "EXPORT")"
    latest_export_result="$(accept_summary_value "${accept_summary}" "LATEST_EXPORT")"
    [[ "${accept_status}" == "SUCCESS" ]] || {
      echo "Target accept status is not SUCCESS: ${accept_status:-<empty>}" >&2
      exit 1
    }
    [[ "${accept_profile_result}" == "${accept_profile}" ]] || {
      echo "Target accept profile mismatch: expected=${accept_profile}, actual=${accept_profile_result:-<empty>}" >&2
      exit 1
    }
    [[ "${accept_full_test_result}" == "${expected_full_test}" ]] || {
      echo "Target full-test evidence mismatch: expected=${expected_full_test}, actual=${accept_full_test_result:-<empty>}" >&2
      exit 1
    }
    [[ "${accept_export_result}" == "False" && "${latest_export_result}" == "-" ]] || {
      echo "Target accept must not own the final export: EXPORT=${accept_export_result:-<empty>}, LATEST_EXPORT=${latest_export_result:-<empty>}" >&2
      exit 1
    }

    echo
    echo "== Closure evidence =="
    python3 "${PROJECT_ROOT}/platform/update/tools/write-target-apply-evidence.py" \
      --patch-zip "${UPDATE_PATCH_ZIP}" \
      --output "${evidence_file}" \
      --target-name "${TARGET_NAME}" \
      --generated-profile "${generated_profile}" \
      --accept-profile "${accept_profile}" \
      --full-test "${expected_full_test}" \
      --source-target-git-head "${source_target_git_head}"

    echo
    echo "== Single target closure export =="
    export_before="$(mktemp)"
    export_after="$(mktemp)"
    find exports/text -maxdepth 1 -type f -name '*.zip' -printf '%f\n' 2>/dev/null | sort > "${export_before}" || true
    ./bin/export.sh full --zip --evidence "${evidence_file}" > "${export_log}"
    target_export_rel="$(tail -n 1 "${export_log}")"
    [[ -n "${target_export_rel}" ]] || {
      echo "Target export command returned no ZIP path." >&2
      exit 1
    }
    latest_export="${TARGET_PATH}/${target_export_rel}"
    [[ -f "${latest_export}" ]] || {
      echo "Target export does not exist: ${latest_export}" >&2
      exit 1
    }
    find exports/text -maxdepth 1 -type f -name '*.zip' -printf '%f\n' 2>/dev/null | sort > "${export_after}" || true
    new_export_count="$(comm -13 "${export_before}" "${export_after}" | sed '/^$/d' | wc -l | tr -d ' ')"
    [[ "${new_export_count}" == "1" ]] || {
      echo "Expected exactly one new target ZIP export, found ${new_export_count}." >&2
      exit 1
    }
    rm -f "${export_before}" "${export_after}"

    python3 ./bin/export-integrity-check.py \
      "${latest_export}" --source-root "${TARGET_PATH}" --require-evidence \
      > "${integrity_log}" 2>&1
    printf 'TARGET_EXPORT=%s\n' "${latest_export}" > "${summary_file}"
  ) > "${apply_log}" 2>&1; then
    target_export=""
    if [[ -f "${summary_file}" ]]; then
      # shellcheck source=/dev/null
      source "${summary_file}"
      target_export="${TARGET_EXPORT:-}"
    fi
    echo "Platform-Update-Target-Apply:"
    echo "  Status:       OK"
    echo "  Target:       ${TARGET_NAME}"
    echo "  Patch-ID:     ${patch_id}"
    echo "  Patch-Scope:  ${patch_scope}"
    echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
    echo "  Target ZIP:   ${target_zip_path}"
    echo "  Delivery:     ${TARGET_DELIVERY_ENABLED:-false}"
    echo "  Producer:     ${producer_preflight_dir}/REPORT.json"
    echo "  Target-Dry:   ${PREFLIGHT_LOG}"
    echo "  Validation:   profile=${accept_profile}, full-test=${expected_full_test}"
    echo "  Accept-Log:   ${accept_log_dir}"
    echo "  Log:          ${apply_log}"
    echo "  Export-Check: ${integrity_log}"
    echo "  Export-Pfad:  ${target_export}"
    echo "  Hinweis:      Zielprojekt wurde genau einmal angewendet; target-apply erzeugte und prüfte genau einen Closure-Export."
    return 0
  fi

  echo "TARGET_EXPORT=" > "${summary_file}"
  echo "Platform-Update-Target-Apply:"
  echo "  Status:       FAILED"
  echo "  Target:       ${TARGET_NAME}"
  echo "  Patch-ID:     ${patch_id}"
  echo "  Patch-Scope:  ${patch_scope}"
  echo "  Source ZIP:   ${UPDATE_PATCH_ZIP}"
  echo "  Target ZIP:   ${target_zip_path}"
  echo "  Producer:     ${producer_preflight_dir}/REPORT.json"
  echo "  Target-Dry:   ${PREFLIGHT_LOG}"
  echo "  Accept-Log:   ${accept_log_dir}"
  echo "  Log:          ${apply_log}"
  echo "  Export-Pfad:  "
  echo "  Hinweis:      Kein Reapply. Zielzustand anhand der Logs prüfen."
  return 1
}


main() {
  local command="${1:-help}"
  case "${command}" in
    -h|--help|help)
      print_usage
      ;;
    list)
      shift
      [[ $# -eq 0 ]] || fail_update "list does not accept arguments"
      list_targets
      ;;
    show)
      shift
      [[ $# -eq 1 ]] || fail_update "show expects exactly one target"
      show_target "$1"
      ;;
    validate)
      shift
      [[ $# -eq 1 ]] || fail_update "validate expects <target|all>"
      validate_targets "$1"
      ;;
    workspace)
      shift
      [[ $# -eq 0 ]] || fail_update "workspace does not accept arguments"
      print_workspace
      ;;
    plan)
      shift
      create_plan "$@"
      ;;
    generate)
      shift
      create_target_plan_patch "$@"
      ;;
    preflight)
      shift
      create_preflight "$@"
      ;;
    compatibility-plan)
      shift
      create_compatibility_plan "$@"
      ;;
    apply-plan)
      shift
      create_apply_plan "$@"
      ;;
    target-apply)
      shift
      create_target_apply "$@"
      ;;
    *)
      fail_update "Unknown command: ${command}"
      ;;
  esac
}

main "$@"

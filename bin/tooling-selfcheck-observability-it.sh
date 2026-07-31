#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LIBRARY="${SCRIPT_DIR}/lib/core/selfcheck-observability.sh"
SELF_CHECK="${SCRIPT_DIR}/tooling-selfcheck.sh"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/tooling-selfcheck-observability-it.XXXXXX")"
trap 'rm -rf "${TMP_ROOT}"' EXIT

fail_test() {
  printf 'TOOLING_SELFCHECK_OBSERVABILITY_IT=FAIL\nDETAIL=%s\n' "$1" >&2
  exit 1
}

[[ -f "${LIBRARY}" ]] || fail_test "observability library missing"
[[ -x "${SELF_CHECK}" ]] || fail_test "tooling selfcheck missing"

before_options="$(set +o)"
# shellcheck source=/dev/null
source "${LIBRARY}"
after_options="$(set +o)"
[[ "${before_options}" == "${after_options}" ]] || fail_test "sourcing changed shell options"

good_command="${TMP_ROOT}/good.sh"
cat > "${good_command}" <<'GOOD'
#!/usr/bin/env bash
printf 'positive-output\n'
GOOD
chmod +x "${good_command}"

export SELF_CHECK_SUBSTEP_LOG_ROOT="${TMP_ROOT}/logs"
positive_out="${TMP_ROOT}/positive.out"
selfcheck_run_substep fixture-positive "${good_command}" >"${positive_out}"
grep -Fx 'SELF_CHECK_SUBSTEP_START=fixture-positive' "${positive_out}" >/dev/null || fail_test "positive start marker missing"
grep -Fx "SELF_CHECK_SUBSTEP_LOG=${TMP_ROOT}/logs/fixture-positive.log" "${positive_out}" >/dev/null || fail_test "positive log marker missing"
grep -Fx 'SELF_CHECK_SUBSTEP_RESULT=fixture-positive:0' "${positive_out}" >/dev/null || fail_test "positive result marker missing"
grep -Fx 'positive-output' "${TMP_ROOT}/logs/fixture-positive.log" >/dev/null || fail_test "positive output not retained"

bad_command="${TMP_ROOT}/bad.sh"
cat > "${bad_command}" <<'BAD'
#!/usr/bin/env bash
printf 'negative-diagnostic\n' >&2
exit 23
BAD
chmod +x "${bad_command}"

negative_out="${TMP_ROOT}/negative.out"
negative_err="${TMP_ROOT}/negative.err"
set +e
selfcheck_run_substep fixture-negative "${bad_command}" >"${negative_out}" 2>"${negative_err}"
negative_rc=$?
set -e
[[ "${negative_rc}" -eq 23 ]] || fail_test "negative exit code was not preserved"
grep -Fx 'SELF_CHECK_SUBSTEP_START=fixture-negative' "${negative_out}" >/dev/null || fail_test "negative start marker missing"
grep -Fx 'SELF_CHECK_SUBSTEP_RESULT=fixture-negative:23' "${negative_out}" >/dev/null || fail_test "negative result marker missing"
grep -Fx 'SELF_CHECK_FAILED_SUBSTEP=fixture-negative' "${negative_err}" >/dev/null || fail_test "failed substep marker missing"
grep -Fx 'negative-diagnostic' "${negative_err}" >/dev/null || fail_test "negative diagnostic not surfaced"
grep -Fx 'negative-diagnostic' "${TMP_ROOT}/logs/fixture-negative.log" >/dev/null || fail_test "negative diagnostic not retained"

for substep in \
  patch-run-api-it \
  patch-transactional-accept-it \
  core-persistence-newness-contract-it \
  patch-state-audit; do
  grep -F "selfcheck_run_substep ${substep} " "${SELF_CHECK}" >/dev/null \
    || fail_test "tooling selfcheck does not register ${substep}"
done

printf 'TOOLING_SELFCHECK_OBSERVABILITY_IT=PASS\n'

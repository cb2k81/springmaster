#!/usr/bin/env bash
# Changelog helper commands for DBTool.

list_changelog_files() {
  local changelog_root="${PROJECT_DIR}/${APP_CHANGELOG_DIR}"
  if [[ ! -d "${changelog_root}" ]]; then
    fail "Changelog directory not found: ${APP_CHANGELOG_DIR}"
  fi
  find "${changelog_root}" -type f | sort | sed "s#^${PROJECT_DIR}/##"
}

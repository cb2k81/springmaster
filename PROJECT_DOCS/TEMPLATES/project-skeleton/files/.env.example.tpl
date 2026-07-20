# __PROJECT_NAME__ local configuration template
APP_NAME=__PROJECT_NAME__
APP_EXPORT_PROJECT_KEY=__PROJECT_NAME__
APP_PORT=__HTTP_PORT__
APP_PROFILE=dev
APP_BASE_PACKAGE=__BASE_PACKAGE__
APP_CORE_PACKAGE=de.cocondo.system

# Database defaults. Copy this file to .env before enabling DB operations.
APP_DB_HOST=localhost
APP_DB_PORT=3306
APP_DEV_DB_NAME=__DB_NAME__
APP_DEV_DB_USER=__DB_NAME__
APP_DEV_DB_PASS=__DB_NAME__
APP_STAGE_DB_NAME=__STAGE_DB_NAME__
APP_STAGE_DB_USER=__DB_NAME__
APP_STAGE_DB_PASS=__DB_NAME__

# MariaDB admin connection for destructive DBTool operations.
APP_DB_ADMIN_USER=root
APP_DB_ADMIN_PASS=

APP_CHANGELOG_DIR=src/main/resources/db/changelog
APP_CHANGELOG_MASTER=src/main/resources/db/changelog/db.changelog-master.xml
APP_LIQUIBASE_CONTEXTS=
APP_LIQUIBASE_ENABLED=false

APP_OPENAPI_PATH=/api-docs
APP_EXPORT_CONFIG_FILE=export.config.json
APP_BUILD_REMOTE_DEPLOY_ENABLED=false
APP_BUILD_CONSOLE_MODE=compact
APP_DIST_DIR=target/dist
APP_DBTOOL_ALLOW_DESTRUCTIVE=false
LOG_LEVEL=INFO

PATCH_SCOPE_ROOT_EXTRA_PATHS="AGENTS.md;contracts/**;src/main/java/de/cocondo/platform/demo/**;src/main/java/de/cocondo/system/entity/**;src/main/java/de/cocondo/system/http/GlobalApiExceptionHandler.java;src/main/java/de/cocondo/system/observability/**;src/main/java/de/cocondo/system/security/**"

# Project-local patch scope extensions. Keep project-specific scopes and paths here,
# not in the shared Springmaster patch tooling. Values are semicolon-separated.
# Extend an existing standard scope:
# PATCH_SCOPE_DEMO_EXTRA_PATHS=src/main/java/com/example/demo/**;src/test/java/com/example/demo/**
# Define additional project-local scopes:
# PATCH_LOCAL_SCOPES=reporting
# PATCH_SCOPE_REPORTING_PATHS=src/main/java/com/example/reporting/**;src/test/java/com/example/reporting/**
# PATCH_SCOPE_REPORTING_LOG_DIR=reporting

# Generated target-project scopes. Keep these values project-local.
# The project-specific scope name matches APP_EXPORT_PROJECT_KEY so patches may
# use scope "__PROJECT_NAME__" without Springmaster hard-coding that name.
PATCH_LOCAL_SCOPES="domain;__PROJECT_NAME__"
PATCH_SCOPE_DOMAIN_PATHS="src/main/java/__BASE_PACKAGE_PATH__/**;src/test/java/__BASE_PACKAGE_PATH__/**;src/main/resources/db/**;PROJECT_DOCS/CONCEPT/**;PROJECT_DOCS/DOMAIN/**"
PATCH_SCOPE_DOMAIN_LOG_DIR=domain
PATCH_SCOPE___PROJECT_SCOPE_ENV___PATHS="src/main/java/__BASE_PACKAGE_PATH__/**;src/test/java/__BASE_PACKAGE_PATH__/**;src/main/resources/db/**;PROJECT_DOCS/CONCEPT/**;PROJECT_DOCS/DOMAIN/**"
PATCH_SCOPE___PROJECT_SCOPE_ENV___LOG_DIR=__PROJECT_NAME__

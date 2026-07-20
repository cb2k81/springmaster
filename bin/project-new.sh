#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

python3 - "$PROJECT_ROOT" "$@" <<'PY'
import argparse
import json
import os
import re
import shutil
import stat
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(sys.argv[1]).resolve()
ARGV = sys.argv[2:]

TEMPLATE_ROOT = PROJECT_ROOT / "PROJECT_DOCS" / "TEMPLATES" / "project-skeleton"
TEMPLATE_FILES = TEMPLATE_ROOT / "files"
PLATFORM_ENV = PROJECT_ROOT / "platform" / "versions" / "platform.env"

TOOLING_FILES = [
    "bin/build.sh",
    "bin/config-contract.py",
    "bin/config-contract.sh",
    "bin/config-contract-it.sh",
    "bin/dbtool.sh",
    "bin/db-migration-contract.py",
    "bin/db-migration-contract.sh",
    "bin/db-migration-contract-it.sh",
    "bin/export-completion.bash",
    "bin/export-integrity-check.py",
    "bin/export-integrity-it.sh",
    "bin/export.sh",
    "bin/init.env.sh",
    "bin/patch-artifact-preflight-it.sh",
    "bin/patch-artifact-preflight.py",
    "bin/patch.py",
    "bin/patch.sh",
    "bin/tooling-selfcheck.sh",
    "bin/lib/core/env.sh",
    "bin/lib/core/log.sh",
    "bin/lib/dbtool/changelog.sh",
    "bin/lib/dbtool/commands.sh",
    "bin/lib/dbtool/config.sh",
    "bin/lib/dbtool/liquibase.sh",
    "bin/lib/dbtool/mariadb.sh",
]

USAGE_EPILOG = """Beispiele:
  ./bin/project-new.sh create --dry-run --name sample --path /tmp/springmaster-sample
  ./bin/project-new.sh create --name sample --path /tmp/springmaster-sample --port 8090

Eigenschaften:
  * Zielpfad darf nicht nicht-leer sein.
  * Es wird keine .env erzeugt.
  * Projektdateien entstehen aus PROJECT_DOCS/TEMPLATES/project-skeleton/files.
  * Tooling-Dateien werden aus dem aktuellen Masterstand übernommen und tokenisiert.
"""


def fail(message: str, code: int = 1):
    print(f"Fehler: {message}", file=sys.stderr)
    sys.exit(code)


def read_env_file(path: Path) -> dict:
    values = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def pascal_case(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value)
    result = "".join(part[:1].upper() + part[1:] for part in parts if part)
    if not result:
        fail(f"Kann keinen Application-Class-Namen aus Projektname ableiten: {value}")
    if result[0].isdigit():
        result = "App" + result
    return result


def validate_name(value: str, field: str):
    if not re.fullmatch(r"[a-z][a-z0-9-]*", value):
        fail(f"{field} muss dem Muster [a-z][a-z0-9-]* entsprechen: {value}")


def validate_db_name(value: str, field: str):
    if not re.fullmatch(r"[a-z][a-z0-9_]*", value):
        fail(f"{field} muss dem Muster [a-z][a-z0-9_]* entsprechen: {value}")


def validate_package(value: str, field: str):
    segment = r"[a-z_][a-z0-9_]*"
    if not re.fullmatch(segment + r"(\." + segment + r")+", value):
        fail(f"{field} muss ein gültiger Java-Paketname mit mindestens zwei Segmenten sein: {value}")


def normalize_env_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()
    return normalized or "PROJECT"


def validate_class_name(value: str):
    if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", value):
        fail(f"application-class muss ein gültiger Java-Klassenname sein und mit Großbuchstaben beginnen: {value}")


def validate_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        fail(f"port muss numerisch sein: {value}")
    if port < 1 or port > 65535:
        fail(f"port muss zwischen 1 und 65535 liegen: {value}")
    return port


def render_text(text: str, tokens: dict) -> str:
    rendered = text
    protected_literals = {
        "springmaster.export-closure-evidence.v1": "__CANONICAL_EXPORT_CLOSURE_SCHEMA__",
        "springmaster.patch-artifact-preflight.v1": "__CANONICAL_PATCH_ARTIFACT_PREFLIGHT_SCHEMA__",
        "springmaster.patch-export-evidence.v1": "__CANONICAL_PATCH_EXPORT_EVIDENCE_SCHEMA__",
        "springmaster.environment-contract.v1": "__CANONICAL_ENVIRONMENT_CONTRACT_SCHEMA__",
        "springmaster.configuration-contract-report.v1": "__CANONICAL_CONFIGURATION_CONTRACT_REPORT_SCHEMA__",
        "springmaster.database-migration-contract.v1": "__CANONICAL_DATABASE_MIGRATION_CONTRACT_SCHEMA__",
        "springmaster.database-migration-contract-report.v1": "__CANONICAL_DATABASE_MIGRATION_CONTRACT_REPORT_SCHEMA__",
    }
    for literal, placeholder in protected_literals.items():
        rendered = rendered.replace(literal, placeholder)
    for key, value in tokens.items():
        rendered = rendered.replace(key, value)

    # Tooling files are copied from Springmaster and tokenized after the template
    # placeholders have been rendered. Replace DB-related defaults before the
    # generic springmaster -> project-name replacement, otherwise projects with
    # hyphens would receive invalid default database/user names when no .env is
    # present. The .env.example template already uses the sanitized DB token.
    tooling_default_replacements = {
        'APP_DEV_DB_NAME="${APP_DEV_DB_NAME:-springmaster}"': f'APP_DEV_DB_NAME="${{APP_DEV_DB_NAME:-{tokens["__DB_NAME__"]}}}"',
        'APP_DEV_DB_USER="${APP_DEV_DB_USER:-springmaster}"': f'APP_DEV_DB_USER="${{APP_DEV_DB_USER:-{tokens["__DB_NAME__"]}}}"',
        'APP_DEV_DB_PASS="${APP_DEV_DB_PASS:-springmaster}"': f'APP_DEV_DB_PASS="${{APP_DEV_DB_PASS:-{tokens["__DB_NAME__"]}}}"',
        'APP_STAGE_DB_NAME="${APP_STAGE_DB_NAME:-${APP_BUILD_DB_NAME:-springmaster_build}}"': f'APP_STAGE_DB_NAME="${{APP_STAGE_DB_NAME:-${{APP_BUILD_DB_NAME:-{tokens["__STAGE_DB_NAME__"]}}}}}"',
    }
    for source, replacement in tooling_default_replacements.items():
        rendered = rendered.replace(source, replacement)

    rendered = rendered.replace("de/cocondo/platform", tokens["__BASE_PACKAGE_PATH__"])
    rendered = rendered.replace("de.cocondo.platform", tokens["__BASE_PACKAGE__"])
    rendered = rendered.replace("springmaster_build", tokens["__STAGE_DB_NAME__"])
    rendered = rendered.replace("springmaster", tokens["__PROJECT_NAME__"])
    for literal, placeholder in protected_literals.items():
        rendered = rendered.replace(placeholder, literal)
    return rendered


def render_path(path: str, tokens: dict) -> str:
    rendered = render_text(path, tokens)
    if rendered.endswith(".tpl"):
        rendered = rendered[:-4]
    return rendered


def is_text_file(path: Path) -> bool:
    try:
        path.read_text(encoding="utf-8")
        return True
    except UnicodeDecodeError:
        return False


def ensure_template_ready():
    if not TEMPLATE_FILES.exists():
        fail(f"Template-Dateien fehlen: {TEMPLATE_FILES}")
    manifest = TEMPLATE_ROOT / "skeleton.manifest.json"
    if not manifest.exists():
        fail(f"Template-Manifest fehlt: {manifest}")


def ensure_target_empty(target: Path):
    if target.exists():
        if not target.is_dir():
            fail(f"Zielpfad existiert und ist kein Verzeichnis: {target}")
        if any(target.iterdir()):
            fail(f"Zielverzeichnis ist nicht leer. Abbruch ohne Überschreiben: {target}")


def collect_plan(target: Path, tokens: dict):
    operations = []

    for source in sorted(TEMPLATE_FILES.rglob("*")):
        if not source.is_file():
            continue
        rel = source.relative_to(TEMPLATE_FILES).as_posix()
        rendered_rel = render_path(rel, tokens)
        operations.append({
            "kind": "template",
            "source": source,
            "target": target / rendered_rel,
            "target_rel": rendered_rel,
        })

    for rel in TOOLING_FILES:
        source = PROJECT_ROOT / rel
        if not source.exists() or not source.is_file():
            fail(f"Erforderliche Tooling-Datei fehlt: {rel}")
        operations.append({
            "kind": "tooling",
            "source": source,
            "target": target / rel,
            "target_rel": rel,
        })

    generated_files = {
        "platform/versions/platform.env": platform_env_content(tokens),
        "PROJECT_DOCS/BOOTSTRAP/PROJECT_NEW_BOOTSTRAP.md": bootstrap_doc_content(tokens),
        "PROJECT_DOCS/CONFIG/ENV_TEMPLATE.env": tokens["__ENV_EXAMPLE_CONTENT__"],
        "patches/logs/bootstrap/CHANGELOG-000001-project-new-bootstrap.md": bootstrap_changelog_content(tokens),
        "patches/archives/000001_project_new_bootstrap/manifest.json": json.dumps(bootstrap_manifest(tokens), indent=2, ensure_ascii=False) + "\n",
        "patches/archives/000001_project_new_bootstrap/patch-log.json": json.dumps(bootstrap_patch_log(tokens), indent=2, ensure_ascii=False) + "\n",
        "tmp/.gitkeep": "",
    }
    for rel, content in generated_files.items():
        operations.append({
            "kind": "generated",
            "content": content,
            "target": target / rel,
            "target_rel": rel,
        })

    return operations


def platform_env_content(tokens: dict) -> str:
    return "".join([
        f"PLATFORM_NAME={tokens['__PROJECT_NAME__']}\n",
        f"PLATFORM_VERSION={tokens['__PLATFORM_VERSION__']}\n",
        f"PLATFORM_CORE_VERSION={tokens['__CORE_VERSION__']}\n",
        f"PLATFORM_TOOLING_VERSION={tokens['__TOOLING_VERSION__']}\n",
        f"PLATFORM_TEMPLATE_VERSION={tokens['__TEMPLATE_VERSION__']}\n",
        "PLATFORM_DEMO_VERSION=0.0.0\n",
        f"PLATFORM_UPDATE_VERSION={tokens['__UPDATE_VERSION__']}\n",
        "PLATFORM_STATE_PATCH=000001_project_new_bootstrap\n",
        "PLATFORM_BASELINE_KIND=project-new\n",
        f"PLATFORM_BASE_PACKAGE={tokens['__BASE_PACKAGE__']}\n",
    ])


def bootstrap_doc_content(tokens: dict) -> str:
    return f"""# Project-New Bootstrap

Dieses Projekt wurde aus dem Springmaster Project Skeleton erzeugt.

```text
PROJECT_NAME={tokens['__PROJECT_NAME__']}
GROUP_ID={tokens['__GROUP_ID__']}
ARTIFACT_ID={tokens['__ARTIFACT_ID__']}
BASE_PACKAGE={tokens['__BASE_PACKAGE__']}
APPLICATION_CLASS={tokens['__APPLICATION_CLASS__']}
HTTP_PORT={tokens['__HTTP_PORT__']}
DB_NAME={tokens['__DB_NAME__']}
STAGE_DB_NAME={tokens['__STAGE_DB_NAME__']}
PLATFORM_VERSION={tokens['__PLATFORM_VERSION__']}
CORE_VERSION={tokens['__CORE_VERSION__']}
TOOLING_VERSION={tokens['__TOOLING_VERSION__']}
TEMPLATE_VERSION={tokens['__TEMPLATE_VERSION__']}
UPDATE_VERSION={tokens['__UPDATE_VERSION__']}
STATE_PATCH=000001_project_new_bootstrap
```

## Standardprüfung

```bash
./bin/patch.sh list
./bin/export.sh full --zip
./bin/dbtool.sh status
mvn test
```
"""


def bootstrap_changelog_content(tokens: dict) -> str:
    return f"""# CHANGELOG 000001 – project-new bootstrap

## Zweck

Initiale Projektanlage für `{tokens['__PROJECT_NAME__']}` aus dem Springmaster Project Skeleton.

## Ergebnis

* Maven-/Spring-Boot-Basis angelegt
* minimale Anwendung angelegt
* Patch-, Export-, Build- und DBTool-Basis angelegt
* `.env.example` angelegt
* keine produktive `.env` erzeugt
"""


def bootstrap_manifest(tokens: dict) -> dict:
    return {
        "schemaVersion": "springmaster.patch-manifest.v2",
        "artifactId": tokens["__BOOTSTRAP_ARTIFACT_ID__"],
        "id": "000001_project_new_bootstrap",
        "patchId": "000001_project_new_bootstrap",
        "name": "project_new_bootstrap",
        "scope": "bootstrap",
        "status": "registered-after-project-new",
        "projectName": tokens["__PROJECT_NAME__"],
        "packageType": "project-new-generated-bootstrap",
    }


def bootstrap_patch_log(tokens: dict) -> dict:
    now = datetime.now(timezone.utc).astimezone().isoformat()
    return {
        "schemaVersion": "springmaster.patch-manifest.v2",
        "artifactId": tokens["__BOOTSTRAP_ARTIFACT_ID__"],
        "patchId": "000001_project_new_bootstrap",
        "patchNumber": "000001",
        "archiveName": "project-new-generated-bootstrap",
        "name": "project new bootstrap",
        "scope": "bootstrap",
        "status": "applied",
        "createdAt": now,
        "projectRoot": "<generated-project-root>",
        "summary": {
            "new": 0,
            "modified": 0,
            "unchanged": 0,
            "deleted": 0,
            "delete_missing": 0,
        },
        "entries": [],
        "manifest": bootstrap_manifest(tokens),
    }


def write_operation(op: dict, tokens: dict):
    target = op["target"]
    target.parent.mkdir(parents=True, exist_ok=True)

    if op["kind"] in ("template", "tooling"):
        source = op["source"]
        if is_text_file(source):
            content = render_text(source.read_text(encoding="utf-8"), tokens)
            target.write_text(content, encoding="utf-8")
        else:
            shutil.copy2(source, target)
    elif op["kind"] == "generated":
        target.write_text(op["content"], encoding="utf-8")
    else:
        fail(f"Unbekannte Operation: {op['kind']}")

    if op["target_rel"].startswith("bin/") and target.suffix in (".sh", ".py"):
        current = target.stat().st_mode
        target.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def build_tokens(args) -> dict:
    platform = read_env_file(PLATFORM_ENV)
    name = args.name
    validate_name(name, "name")

    artifact_id = args.artifact_id or name
    validate_name(artifact_id, "artifact-id")

    default_package_suffix = name.replace("-", "")
    group_id = args.group_id or f"de.cocondo.{default_package_suffix}"
    validate_package(group_id, "group-id")

    base_package = args.base_package or group_id
    validate_package(base_package, "base-package")

    db_name = args.db_name or name.replace("-", "_")
    validate_db_name(db_name, "db-name")

    stage_db_name = args.stage_db_name or f"{db_name}_build"
    validate_db_name(stage_db_name, "stage-db-name")

    application_class = args.application_class or f"{pascal_case(name)}Application"
    validate_class_name(application_class)

    port = validate_port(str(args.port))
    base_package_path = base_package.replace(".", "/")

    platform_version = args.platform_version or platform.get("PLATFORM_VERSION", "0.1.0-bootstrap")
    core_version = args.core_version or platform.get("PLATFORM_CORE_VERSION", "0.0.0")
    tooling_version = args.tooling_version or platform.get("PLATFORM_TOOLING_VERSION", "0.1.0-bootstrap")
    template_version = platform.get("PLATFORM_TEMPLATE_VERSION", "0.0.0")
    update_version = platform.get("PLATFORM_UPDATE_VERSION", "0.0.0")

    env_example = "".join([
        f"# {name} local configuration template\n",
        f"APP_NAME={name}\n",
        f"APP_EXPORT_PROJECT_KEY={name}\n",
        f"APP_PORT={port}\n",
        "APP_PROFILE=dev\n",
        f"APP_BASE_PACKAGE={base_package}\n",
        "APP_CORE_PACKAGE=de.cocondo.system\n",
        "\n",
        "# Database defaults. Copy this file to .env before enabling DB operations.\n",
        "APP_DB_HOST=localhost\n",
        "APP_DB_PORT=3306\n",
        f"APP_DEV_DB_NAME={db_name}\n",
        f"APP_DEV_DB_USER={db_name}\n",
        f"APP_DEV_DB_PASS={db_name}\n",
        f"APP_STAGE_DB_NAME={stage_db_name}\n",
        f"APP_STAGE_DB_USER={db_name}\n",
        f"APP_STAGE_DB_PASS={db_name}\n",
        "\n",
        "# MariaDB admin connection for destructive DBTool operations.\n",
        "APP_DB_ADMIN_USER=root\n",
        "APP_DB_ADMIN_PASS=\n",
        "\n",
        "APP_CHANGELOG_DIR=src/main/resources/db/changelog\n",
        "APP_CHANGELOG_MASTER=src/main/resources/db/changelog/db.changelog-master.xml\n",
        "APP_LIQUIBASE_CONTEXTS=\n",
        "APP_LIQUIBASE_ENABLED=false\n",
        "\n",
        "APP_OPENAPI_PATH=/api-docs\n",
        "APP_EXPORT_CONFIG_FILE=export.config.json\n",
        "APP_BUILD_REMOTE_DEPLOY_ENABLED=false\n",
        "APP_BUILD_CONSOLE_MODE=compact\n",
        "APP_DIST_DIR=target/dist\n",
        "APP_DBTOOL_ALLOW_DESTRUCTIVE=false\n",
        "LOG_LEVEL=INFO\n",
        "\n",
        "PATCH_SCOPE_ROOT_EXTRA_PATHS=\"AGENTS.md;contracts/**;src/main/java/de/cocondo/system/http/GlobalApiExceptionHandler.java;src/main/java/de/cocondo/system/observability/**\"\n",
        "\n",
        "# Generated target-project scopes. Keep these values project-local.\n",
        f"PATCH_LOCAL_SCOPES=\"domain;{name}\"\n",
        f"PATCH_SCOPE_DOMAIN_PATHS=\"src/main/java/{base_package_path}/**;src/test/java/{base_package_path}/**;src/main/resources/db/**;PROJECT_DOCS/CONCEPT/**;PROJECT_DOCS/DOMAIN/**\"\n",
        "PATCH_SCOPE_DOMAIN_LOG_DIR=domain\n",
        f"PATCH_SCOPE_{normalize_env_name(name)}_PATHS=\"src/main/java/{base_package_path}/**;src/test/java/{base_package_path}/**;src/main/resources/db/**;PROJECT_DOCS/CONCEPT/**;PROJECT_DOCS/DOMAIN/**\"\n",
        f"PATCH_SCOPE_{normalize_env_name(name)}_LOG_DIR={name}\n",
    ])

    project_scope_env = normalize_env_name(name)

    return {
        "__PROJECT_NAME__": name,
        "__ARTIFACT_ID__": artifact_id,
        "__BOOTSTRAP_ARTIFACT_ID__": f"urn:uuid:{uuid.uuid4()}",
        "__GROUP_ID__": group_id,
        "__BASE_PACKAGE__": base_package,
        "__BASE_PACKAGE_PATH__": base_package_path,
        "__APPLICATION_CLASS__": application_class,
        "__HTTP_PORT__": str(port),
        "__DB_NAME__": db_name,
        "__STAGE_DB_NAME__": stage_db_name,
        "__PROJECT_SCOPE_ENV__": project_scope_env,
        "__PLATFORM_VERSION__": platform_version,
        "__CORE_VERSION__": core_version,
        "__TOOLING_VERSION__": tooling_version,
        "__TEMPLATE_VERSION__": template_version,
        "__UPDATE_VERSION__": update_version,
        "__ENV_EXAMPLE_CONTENT__": env_example,
    }


def create_command(args):
    ensure_template_ready()
    target = Path(args.path).expanduser().resolve()
    tokens = build_tokens(args)
    operations = collect_plan(target, tokens)

    print("Project-New:")
    print(f"  Master:       {PROJECT_ROOT}")
    print(f"  Ziel:         {target}")
    print(f"  Projekt:      {tokens['__PROJECT_NAME__']}")
    print(f"  Package:      {tokens['__BASE_PACKAGE__']}")
    print(f"  Modus:        {'DRY-RUN' if args.dry_run else 'AUSFÜHREN'}")
    print()

    if target.exists() and any(target.iterdir()):
        fail(f"Zielverzeichnis ist nicht leer. Abbruch ohne Überschreiben: {target}")

    for op in operations:
        marker = "[PLAN]" if args.dry_run else "[WRITE]"
        print(f"  {marker:<10}{op['target_rel']}")

    print()
    print(f"Zusammenfassung: {len(operations)} Dateien")

    if args.dry_run:
        print("Dry-run abgeschlossen. Es wurden keine Dateien geschrieben.")
        return

    ensure_target_empty(target)
    target.mkdir(parents=True, exist_ok=True)
    for op in operations:
        write_operation(op, tokens)

    print("Projektanlage abgeschlossen.")
    print()
    print("Nächste Prüfung:")
    print(f"  cd {target}")
    print("  ./bin/patch.sh list")
    print("  ./bin/export.sh full --zip")
    print("  ./bin/dbtool.sh status")
    print("  mvn test")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="project-new.sh",
        description="Erzeugt neue Cocondo Java-Backend-Projekte aus dem Springmaster Project Skeleton.",
        epilog=USAGE_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    create = sub.add_parser("create", help="Projekt erzeugen", formatter_class=argparse.RawDescriptionHelpFormatter)
    create.add_argument("--dry-run", action="store_true", help="nur Plan anzeigen, keine Dateien schreiben")
    create.add_argument("--name", required=True, help="Projektname, z. B. sample")
    create.add_argument("--path", required=True, help="Zielpfad, muss leer oder nicht vorhanden sein")
    create.add_argument("--artifact-id", help="Maven artifactId, Default: --name")
    create.add_argument("--group-id", help="Maven groupId, Default: de.cocondo.<name ohne Bindestriche>")
    create.add_argument("--base-package", help="Java-Basispaket, Default: groupId")
    create.add_argument("--application-class", help="Spring-Boot-Application-Klasse, Default: <NamePascalCase>Application")
    create.add_argument("--port", default="8080", help="HTTP-Port, Default: 8080")
    create.add_argument("--db-name", help="Datenbankname, Default: name mit '_' statt '-'")
    create.add_argument("--stage-db-name", help="Stage-/Build-Datenbankname, Default: <db-name>_build")
    create.add_argument("--platform-version", help="explizite Platform-Version")
    create.add_argument("--core-version", help="explizite Core-Version")
    create.add_argument("--tooling-version", help="explizite Tooling-Version")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args(ARGV)
    if args.command == "create":
        create_command(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
PY

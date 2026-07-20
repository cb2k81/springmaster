#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

SCHEMA = "springmaster.environment-contract.v1"
NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
JAVA_PACKAGE = re.compile(r"^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)+$")
DB_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


def parse_env(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if NAME.fullmatch(key):
            result[key] = value.strip().strip('"')
    return result


def validate_value(item: dict, value: str) -> str | None:
    kind = item["type"]
    if kind == "integer":
        try:
            number = int(value)
        except ValueError:
            return "not-integer"
        if "minimum" in item and number < item["minimum"]:
            return "below-minimum"
        if "maximum" in item and number > item["maximum"]:
            return "above-maximum"
    elif kind == "boolean" and value not in {"true", "false"}:
        return "not-boolean"
    elif kind == "enum" and value not in set(item.get("allowed", [])):
        return "not-allowed"
    elif kind == "java-package" and not JAVA_PACKAGE.fullmatch(value):
        return "not-java-package"
    elif kind == "database-identifier" and not DB_IDENTIFIER.fullmatch(value):
        return "not-database-identifier"
    elif kind == "relative-path" and (not value or value.startswith("/") or ".." in Path(value).parts):
        return "not-safe-relative-path"
    elif kind == "http-path" and (not value.startswith("/") or " " in value):
        return "not-http-path"
    elif kind == "string" and item.get("required") and not value:
        return "empty-required-string"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--contract", default="contracts/configuration/environment-contract.json")
    parser.add_argument("--out", default="target/config-contract-report.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    contract_path = root / args.contract
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    findings: list[dict[str, object]] = []
    if contract.get("schema") != SCHEMA:
        findings.append({"code": "CONTRACT_SCHEMA_INVALID", "actual": contract.get("schema")})
    variables = contract.get("variables")
    if not isinstance(variables, list) or not variables:
        findings.append({"code": "VARIABLES_MISSING"})
        variables = []
    by_name: dict[str, dict] = {}
    for item in variables:
        name = item.get("name")
        if not isinstance(name, str) or not NAME.fullmatch(name):
            findings.append({"code": "VARIABLE_NAME_INVALID", "name": name})
            continue
        if name in by_name:
            findings.append({"code": "VARIABLE_DUPLICATE", "name": name})
        by_name[name] = item
        default = str(item.get("default", ""))
        reason = validate_value(item, default)
        if reason:
            findings.append({"code": "DEFAULT_INVALID", "name": name, "reason": reason})
        if item.get("secret") and item.get("productionDefaultAllowed") is not False:
            findings.append({"code": "SECRET_PRODUCTION_POLICY_MISSING", "name": name})
    sources = contract.get("sources", {})
    defaults_path = root / sources.get("defaults", ".env.example")
    documented_path = root / sources.get("documentedTemplate", "PROJECT_DOCS/CONFIG/SPRINGMASTER_ENV_TEMPLATE.env")
    shell_path = root / sources.get("shellLoader", "bin/lib/core/env.sh")
    spring_path = root / sources.get("springRuntime", "src/main/resources/application.yml")
    for path, code in ((defaults_path, "DEFAULTS_FILE_MISSING"), (documented_path, "DOCUMENTED_TEMPLATE_MISSING"), (shell_path, "SHELL_LOADER_MISSING"), (spring_path, "SPRING_CONFIG_MISSING")):
        if not path.is_file():
            findings.append({"code": code, "path": path.relative_to(root).as_posix()})
    if defaults_path.is_file() and documented_path.is_file():
        defaults = parse_env(defaults_path)
        documented = parse_env(documented_path)
        expected = {name: str(item.get("default", "")) for name, item in by_name.items()}
        allowed_prefixes = tuple(str(value) for value in contract.get("allowedUndeclaredPrefixes", []))
        for label, values in (("defaults", defaults), ("documented", documented)):
            for name in sorted(expected.keys() - values.keys()):
                findings.append({"code": "VARIABLE_MISSING", "source": label, "name": name})
            for name in sorted(values.keys() - expected.keys()):
                if not allowed_prefixes or not name.startswith(allowed_prefixes):
                    findings.append({"code": "VARIABLE_UNDECLARED", "source": label, "name": name})
            for name in sorted(expected.keys() & values.keys()):
                if values[name] != expected[name]:
                    findings.append({"code": "DEFAULT_DRIFT", "source": label, "name": name, "expected": expected[name], "actual": values[name]})
    if shell_path.is_file():
        shell = shell_path.read_text(encoding="utf-8")
        export_section = shell.rsplit("\nexport ", 1)[-1] if "\nexport " in shell else ""
        for name in sorted(by_name):
            if not re.search(rf"^{re.escape(name)}=", shell, re.MULTILINE):
                findings.append({"code": "SHELL_NORMALIZATION_MISSING", "name": name})
            if not re.search(rf"\b{re.escape(name)}\b", export_section):
                findings.append({"code": "SHELL_EXPORT_MISSING", "name": name})
    if spring_path.is_file():
        spring = spring_path.read_text(encoding="utf-8")
        for name in ("APP_PORT", "APP_PROFILE", "APP_OPENAPI_PATH", "LOG_LEVEL"):
            if "${" + name not in spring:
                findings.append({"code": "SPRING_PLACEHOLDER_MISSING", "name": name})
    report = {
        "schema": "springmaster.configuration-contract-report.v1",
        "status": "PASS" if not findings else "FAIL",
        "contract": args.contract,
        "variableCount": len(by_name),
        "findings": findings,
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"CONFIG_CONTRACT={report['status']}")
    print(f"REPORT={out}")
    return 1 if args.check and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

SCHEMA = "springmaster.http-observability-contract.v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--contract", default="contracts/observability/http-observability-contract.json")
    parser.add_argument("--out", default="target/observability-contract-report.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    contract = json.loads((root / args.contract).read_text(encoding="utf-8"))
    findings: list[dict[str, object]] = []
    if contract.get("schema") != SCHEMA:
        findings.append({"code": "CONTRACT_SCHEMA_INVALID", "actual": contract.get("schema")})
    correlation = contract.get("correlation", {})
    filter_path = root / "src/main/java/de/cocondo/system/observability/CorrelationIdFilter.java"
    support_path = root / "src/main/java/de/cocondo/system/observability/CorrelationIdSupport.java"
    handler_path = root / "src/main/java/de/cocondo/system/http/GlobalApiExceptionHandler.java"
    app_path = root / "src/main/resources/application.yml"
    for path, code in ((filter_path, "FILTER_MISSING"), (support_path, "SUPPORT_MISSING"), (handler_path, "ERROR_HANDLER_MISSING"), (app_path, "APPLICATION_CONFIG_MISSING")):
        if not path.is_file():
            findings.append({"code": code, "path": path.relative_to(root).as_posix()})
    if support_path.is_file():
        source = support_path.read_text(encoding="utf-8")
        for value, code in (
            (correlation.get("header"), "HEADER_CONSTANT_DRIFT"),
            (correlation.get("requestAttribute"), "REQUEST_ATTRIBUTE_DRIFT"),
            (correlation.get("mdcKey"), "MDC_KEY_DRIFT"),
        ):
            if not isinstance(value, str) or f'"{value}"' not in source:
                findings.append({"code": code, "expected": value})
    if handler_path.is_file() and "CorrelationIdSupport.from(request)" not in handler_path.read_text(encoding="utf-8"):
        findings.append({"code": "ERROR_HANDLER_CORRELATION_LOOKUP_MISSING"})
    if app_path.is_file():
        config = app_path.read_text(encoding="utf-8")
        required_markers = {
            "MANAGEMENT_EXPOSURE_DRIFT": "include: health,info",
            "HEALTH_DETAILS_NOT_HARDENED": "show-details: never",
            "HEALTH_COMPONENTS_NOT_HARDENED": "show-components: never",
            "ERROR_EXCEPTION_NOT_HARDENED": "include-exception: false",
            "ERROR_MESSAGE_NOT_HARDENED": "include-message: never",
            "ERROR_STACKTRACE_NOT_HARDENED": "include-stacktrace: never",
            "ERROR_BINDING_NOT_HARDENED": "include-binding-errors: never",
            "MDC_LOG_PATTERN_MISSING": "%X{correlationId:-}",
        }
        for code, marker in required_markers.items():
            if marker not in config:
                findings.append({"code": code, "marker": marker})
    report = {
        "schema": "springmaster.observability-contract-report.v1",
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OBSERVABILITY_CONTRACT={report['status']}")
    print(f"REPORT={out}")
    return 1 if args.check and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

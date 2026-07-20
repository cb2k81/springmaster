---
documentType: adr
status: accepted
scope: observability-and-error-trace
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# ADR-0010: Observability and Error Trace Strategy

## Context

Springmaster exposed Actuator health and info endpoints and already modeled optional `correlationId` and `traceId` error fields. It did not yet create a request correlation identifier, propagate it to logs and responses, or define safe management/error defaults.

## Decision

1. Every HTTP request receives one opaque correlation identifier.
2. The canonical header is `X-Correlation-Id`. A syntactically valid inbound value is propagated; missing or invalid values are replaced with a generated UUID.
3. The correlation identifier is stored in request attribute `springmaster.correlationId`, SLF4J MDC key `correlationId`, the response header and API error responses.
4. MDC state is always restored or removed after request processing, including exceptional paths.
5. `traceId` remains reserved for an explicitly adopted tracing implementation. Springmaster does not synthesize or publicly expose a fake trace identifier.
6. Public error responses never expose stack traces, exception class names, SQL details or binding internals.
7. The default management exposure remains limited to `health` and `info`. Health details and components are not public by default.
8. Logs include the correlation identifier but must not log secrets, credentials, authorization tokens or complete request bodies by default.
9. `contracts/observability/http-observability-contract.json` is the machine-readable baseline; its validator checks runtime configuration and implementation markers.
10. Distributed tracing, metrics backends, audit-event retention and production log shipping require later explicit decisions and operational ownership.

## Consequences

- Support can correlate a client-visible error with server logs without exposing internal trace data.
- Correlation is implemented in reusable Core code under `de.cocondo.system.observability`.
- Management endpoint hardening is a runtime default, not a replacement for network-level access control.

## Verification

```bash
cd /opt/cocondo/springmaster || exit 1
./bin/observability-contract.sh --check
./bin/observability-contract-it.sh
mvn -q -Dtest=CorrelationIdFilterTest,CorrelationIdWebContractTest,GlobalApiExceptionHandlerTest test
```

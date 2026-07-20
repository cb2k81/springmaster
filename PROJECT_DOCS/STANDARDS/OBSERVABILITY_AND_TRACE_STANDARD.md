---
documentType: requirements
status: active
scope: runtime-observability
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Observability and Trace Standard

## HTTP correlation

- Header: `X-Correlation-Id`.
- Accepted inbound syntax: 1 to 128 characters from `A-Z`, `a-z`, `0-9`, `.`, `_` and `-`.
- Missing, blank or invalid values are replaced by a generated UUID.
- The final value is returned in the response header and placed in MDC key `correlationId` for the duration of request processing.
- API error responses use the final correlation identifier. They do not copy an unvalidated inbound header.

## Trace identifiers

`traceId` is reserved for a real tracing implementation. It is not derived from the correlation identifier and is not populated with a random compatibility value. Public exposure requires a later decision that the identifier is opaque and safe.

## Safe runtime defaults

- Actuator web exposure: `health,info` only.
- Health details and components: `never` by default.
- Error stack traces, exception class names, messages and binding errors: not included by the default error endpoint.
- Request bodies, credentials and secret environment values are not logged by default.

## Operational boundary

This standard supplies a local correlation baseline. It does not establish distributed tracing, metrics retention, alert thresholds, audit retention or external log shipping. Those capabilities require environment-specific ownership and qualification.

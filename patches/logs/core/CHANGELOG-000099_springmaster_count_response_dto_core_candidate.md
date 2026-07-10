# 000099_springmaster_count_response_dto_core_candidate

Scope: core

## Summary

Introduces the reusable Core `CountResponseDTO` for the optional count-only API response shape documented in `000098_springmaster_count_response_contract_candidate`.

## Runtime

- added `src/main/java/de/cocondo/system/dto/CountResponseDTO.java`
- added `src/test/java/de/cocondo/system/dto/CountResponseDTOTest.java`
- extended Core DTO marker tests with count response evidence

## Contract

- public shape remains `{ "totalElements": 0 }`
- `totalElements` is represented as primitive `long`
- negative values are rejected by constructor and setter
- no filter, sort, paging, security or persistence semantics are introduced in the DTO

## Verification

Runner executes targeted DTO tests, full Maven test and full ZIP export.

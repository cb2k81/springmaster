# Patch Archive and Rollback Policy

## Purpose

The patch system applies repository changes safely and reproducibly. It is not a product documentation or audit database.

## Identity

New artifacts carry two identities:

- `artifactId`: immutable and independent from repository sequence;
- `patchId`: local apply sequence required by the current legacy engine.

Only `artifactId` identifies the delivered ZIP globally. `patchId` remains repository provenance and must not appear in product contracts or ADR decisions.

## Transaction data

Patch ZIP, baseline hashes of directly changed files, sandbox output, status markers and test logs are transaction data. They are retained only until the change is committed and qualified, unless release or audit requirements explicitly require longer retention.

## Archives and rollback

Before commit, local archives and backups support rollback. After a qualified commit, Git is the canonical rollback boundary. Rollback must not overwrite later changes silently; the future engine cutover must verify the current after-state before restoration.

## Changelog transition

The current engine still requires one minimal `CHANGELOG` file. This is a bootstrap constraint, not the target policy. The manifest becomes the sole mandatory machine-readable transaction summary in the next engine wave.

## Export boundary

Normal baseline exports exclude patch and validation history. Patch Context and Audit are explicit profiles. Apply and qualification do not automatically require an export.

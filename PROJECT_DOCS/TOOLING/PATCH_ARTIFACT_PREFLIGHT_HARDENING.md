# Patch Artifact Preflight Hardening

## Status

Implemented by:

```text
000124_springmaster_patch_artifact_preflight_hardening
```

Output-directory collision repair:

```text
000132_springmaster_patch_artifact_preflight_output_collision_repair
```

## Purpose

This hardening closes the gap between a structurally valid patch ZIP and a patch artifact that is safe to deliver against the exact committed repository baseline.

The previous live-baseline guard correctly rejected stale SHA-256 assumptions on the target host. It could not prevent an artifact author from deriving those hashes from a text-export reconstruction whose presentation separators had changed the reconstructed bytes. In addition, whitespace and EOF defects could remain hidden until a late `git diff --check`, and the full export did not contain an authoritative raw-byte source manifest.

The artifact preflight therefore treats these concerns as one delivery boundary:

```text
clean committed baseline
-> ZIP identity and scope
-> complete live hashes
-> payload hygiene
-> live dry-run
-> isolated test-copy apply
-> exact changed-path and payload verification
-> git diff --check
-> one full export
-> export raw-byte integrity verification
```

## Command

```bash
./bin/patch.sh artifact-preflight <patch.zip>
```

Options:

```text
--output <dir>       write evidence to a selected directory
--no-export         skip only the test-copy full export
--keep-test-copy    retain the isolated Git worktree for diagnostics
```

The default output is written below:

```text
build/patch-artifact-preflight/<timestamp>_<patch-id>_<random-suffix>/
```

The default directory is allocated atomically with `tempfile.mkdtemp`. The timestamp and patch ID remain readable evidence attributes, while the random suffix guarantees that concurrent or same-second invocations cannot claim the same path. An explicit `--output` path remains exclusive and fails closed when the selected directory already exists.

The command never applies the patch to the live working tree.

## Mandatory baseline

Artifact preflight requires:

* a Git repository;
* a clean working tree including untracked, non-ignored files;
* a complete `manifest.baseline.expectedBeforeSha256` map;
* one baseline entry for every patch operation;
* `null` for every genuinely new path;
* no hash entries without a patch operation;
* no unchanged or already-missing operations.

A Full Text Export is not a byte-preserving source representation. The raw-byte SHA-256 values in the export metadata are authoritative. Text separators, rendered line endings and blank lines in the `.txt` representation must never be used to calculate `expectedBeforeSha256`.

## Payload hygiene

Every UTF-8 text payload is checked before the live dry-run.

Rejected conditions:

| Error | Meaning |
|---|---|
| `PATCH_PAYLOAD_CRLF_FORBIDDEN` | CR or CRLF exists in a text payload |
| `PATCH_PAYLOAD_FINAL_NEWLINE_MISSING` | non-empty text payload has no final LF |
| `PATCH_PAYLOAD_EOF_BLANK_LINE` | text payload ends with an additional blank line |
| `PATCH_PAYLOAD_TRAILING_WHITESPACE` | a line ends with spaces or tabs |

Binary payloads are not converted and are verified byte-for-byte after test-copy apply. For every payload, the Git executable class declared in the ZIP metadata must match the applied target: non-executable `100644` or executable `100755`. Host-specific group-write bits such as `0664` and `0775` are preserved and are not treated as Git-mode drift. This applies to `.bash` and other executable file types, not only `.sh` or `.py`.

## Isolated test-copy qualification

The command creates a detached Git worktree at the current `HEAD`, copies the project-local `.env` when present and executes:

```text
live-baseline
apply --dry-run
apply
show latest
payload byte and Git executable-class comparison
git changed-path comparison
git diff --check
full ZIP export
export integrity check
```

The set of changed source paths must equal the operation targets exactly. Patch archives, runtime locks, exports and preflight reports remain ignored runtime evidence and do not widen the source scope.

The worktree is removed automatically unless `--keep-test-copy` is supplied.

## Export format version 2

Every profile metadata file now contains:

```json
{
  "exportFormatVersion": 2,
  "exportStatus": "COMPLETE",
  "sourceHashPolicy": "sha256-raw-repository-bytes",
  "fileManifest": [
    {
      "path": "bin/patch.py",
      "sizeBytes": 12345,
      "sha256": "..."
    }
  ],
  "fileManifestSha256": "...",
  "sourceGit": {
    "available": true,
    "head": "...",
    "branch": "main",
    "dirty": false
  }
}
```

`fileManifest` is calculated directly from the source files as raw bytes before the text representation is written. Its canonical digest prevents silent manifest modification.

The text export repeats source size and SHA-256 in every file header for review convenience, but the JSON metadata remains authoritative.

## Closure evidence

A runner can provide prior-gate evidence without creating a second full export:

```bash
./bin/export.sh full --zip --evidence <evidence.json>
```

Alternatively:

```bash
PATCH_EXPORT_EVIDENCE_FILE=<evidence.json> ./bin/export.sh full --zip
```

The exporter embeds `closure-evidence.json` with:

* the source evidence object;
* a canonical SHA-256 of that object;
* `exportStatus=COMPLETE` written by the exporter;
* the export timestamp.

This distinguishes the export's own completion from a runner status file that may be updated only after the ZIP has been created. One export remains sufficient. Mutable `patches/logs/validation/**` files are excluded from the source profile, so status, summary and export logs may continue to change without falsifying the immutable export manifest.

## Export integrity verification

```bash
python3 bin/export-integrity-check.py \
  <full-export.zip> \
  --source-root . \
  --require-evidence
```

The check validates:

* ZIP CRC integrity;
* export format and completion status;
* included-file and file-manifest parity;
* manifest count and canonical digest;
* raw source size and SHA-256;
* text export member presence;
* optional mandatory closure evidence and its digest.

`bin/export-integrity-it.sh` contains positive, tampered-manifest and mutable-validation-path negative fixtures. `tooling-selfcheck.sh` uses the path of the one export it already creates and does not generate a second export.

## Fail-closed fixtures

`bin/patch-artifact-preflight-it.sh` proves:

* a valid artifact passes twice in immediate succession with distinct report directories;
* the atomic allocator remains collision-free even when both allocations use an identical fixed timestamp;
* a wrong live baseline hash fails;
* trailing whitespace fails;
* an extra EOF blank line fails;
* a missing final newline fails;
* a dirty Git baseline fails;
* Git executable metadata is preserved for a `.bash` payload on group-writable repositories (`0664`/`0775`);
* a mode-only `100644` to `100755` operation is classified as a real modification;
* the live fixture repository remains unchanged.

The Maven contract test `SpringmasterPatchArtifactPreflightTest` executes the artifact and export integrity fixtures.

## Delivery rule

A patch may be described as artifact-qualified only when the report contains:

```text
ARTIFACT_PREFLIGHT=PASS
```

and the report identifies the source patch SHA-256 and source Git `HEAD`.

Host-side targeted tests, full tests and the actual apply remain separate acceptance gates. Artifact preflight does not replace them and must not be cited as proof that host Maven tests were executed.

## Project-New-Verteilung

`project-new.sh` übernimmt Artifact-Preflight, Exportintegritätscheck und beide Integrationstests vollständig in neue Backend-Skeletons. Die Instantiation Acceptance beweist, dass die referenzierten Dateien vorhanden sind, der generierte Export den Integritätscheck besteht und die kanonischen `springmaster.*.v1`-Schema-IDs nicht durch Projekttokenisierung verändert werden.

## Externer Producer-Engine seit 000129

Für einen Tooling-Cutover kann das Zielprojekt noch einen älteren Patch-Engine
besitzen. Der Artifact Preflight unterstützt deshalb zusätzlich:

```bash
python3 bin/patch-artifact-preflight.py \
  /path/to/target \
  /path/to/target-bound-patch.zip \
  --no-export \
  --engine /path/to/springmaster/bin/patch.py
```

Der angegebene Engine wird mit dem Zielprojektroot aufgerufen und auch für den
isolierten Worktree-Apply verwendet. Das Zielrepository wird nicht verändert.
Die Option ist ausschließlich eine Producer-Qualifikation; sie ersetzt keinen
Tooling-Apply im Zielprojekt.

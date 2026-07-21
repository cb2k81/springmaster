# 000163_springmaster_catalogitem_persistent_candidate_runtime

Artifact ID: `urn:uuid:eb6ad3e5-8f51-4192-a62a-61a2e8dd33b8`

## Ziel

Den CatalogItem Candidate als kleinsten vollständigen persistenten JPA-Schnitt auf der akzeptierten `000160`-Baseline implementieren, ohne Canonicalization, Security-Promotion oder Zielprojektmutation vorwegzunehmen.

## Provenienz der Neuauflage

Die Artefakte `000159_springmaster_catalogitem_persistent_candidate_runtime`, `000161_springmaster_catalogitem_persistent_candidate_runtime` und `000162_springmaster_catalogitem_persistent_candidate_runtime` wurden nicht akzeptiert:

- `000159` brach vor dem ersten Maven-Test wegen eines unbeschränkten Validation-Logdateinamens ab; `000160_springmaster_patch_accept_bounded_validation_log_names` schloss diese Tooling-Schuld.
- `000161` erreichte die gezielten Maven-Tests, scheiterte jedoch an einer gemeinsam benannten H2-In-Memory-Datenbank: ein späterer Spring-ApplicationContext traf auf die bereits initialisierte Liquibase-Tabelle `databasechangelog`.
- `000162` isolierte die H2-Datenbank pro ApplicationContext erfolgreich. Im gezielten Lauf bestanden alle CatalogItem-, OpenAPI- und Controller-Tests. Nur der neue Isolationstest scheiterte, weil er fälschlich erwartete, dass H2 JDBC-Metadaten die URL-Optionen `MODE=MariaDB` und `DATABASE_TO_LOWER=TRUE` zurückgeben.

Dieses Artefakt ist eine neu identifizierte Neuauflage auf derselben akzeptierten `000160`-Baseline. Es verwendet eine neue globale Artifact-ID, übernimmt keine Acceptance-Behauptung aus den fehlgeschlagenen Artefakten und korrigiert ausschließlich die Beobachtungsgrenze des Isolationstests.

## Änderungen

- In-Memory-Runtime durch Spring-Data-JPA-Repository, Criteria-Query-Adapter und transaktionalen Service ersetzt.
- Paging- und Sortierwerte werden vor Pageable-/JPA-Konstruktion validiert; Offset-Überlauf liefert den bestehenden `400 INVALID_REQUEST`-Vertrag.
- Liquibase-Schema für CatalogItem und Tags ergänzt; H2-Testprofil mit Liquibase und Hibernate-Schema-Validation aktiviert.
- H2-Datenbanknamen werden pro Spring-ApplicationContext über `${random.uuid}` isoliert, während `MODE=MariaDB` und `DATABASE_TO_LOWER=TRUE` erhalten bleiben.
- `TestDatabaseIsolationContractTest` prüft die konfigurierten URLs auf Kompatibilitätsoptionen, die JDBC-Metadaten auf unterschiedliche Laufzeit-Datenbankidentitäten und beide Datenbanken auf erfolgreiche Liquibase-Initialisierung.
- `DomainEntity.persistenceVersion` atomar auf `null -> 0 -> 1` umgestellt und durch Persistenzvertragstests abgesichert.
- Query-, Detail/Lookup- und Write-Report-Tooling an die persistente Runtime angepasst; Golden Evidence aktualisiert.
- Aktive Verträge, Evidence, Dokumentation und technische-Schulden-Prüfung auf denselben Candidate-Status gebracht.

## Verifikation vor Artefakterstellung

Erfolgreich:

- JSON-, XML- und YAML-Parsing;
- Python-Syntaxprüfungen;
- Core-Persistence-Newness Contract und Negativ-IT;
- Configuration Contract und Negativ-IT;
- DB-Migration Contract und Negativ-IT;
- Documentation Gate und Negativ-IT;
- Query-, Detail/Lookup-, Request-Validation- und Write-Report gegen Golden Fixtures;
- Springmaster Report-only Gates ohne Blocker oder Errors;
- `git diff --check`;
- Patch-Live-Baseline, Dry-run und Artifact-Preflight in einer isolierten Baselinekopie.

In der Erstellungsumgebung ist Maven nicht verfügbar. Das Artefakt darf daher erst nach grünem gezieltem Maven-Lauf einschließlich `TestDatabaseIsolationContractTest`, vollständigem Maven-Test und Springmaster-Gates akzeptiert und committed werden.

## Technische Schulden und Roadmap-Gate

Die durch `000161` sichtbar gewordene gemeinsame H2-Testdatenbank bleibt geschlossen. Die durch `000162` sichtbar gewordene falsche Annahme über JDBC-Metadaten wird im Test korrigiert, ohne die Produktkonfiguration abzuschwächen. Keine neue Produkt- oder Zielprojektschuld wird akzeptiert. Explizite Restblocker bleiben MariaDB-/Constraint- und Optimistic-Lock-Qualifikation, Management-Security, Canonicalization, Core-Artefaktisierung und Generated-Slice-Delivery. Die grobe äußere Fehlerklassifikation `worktree-validation` bleibt als getrennte Tooling-Diagnostikschuld dokumentiert.

Der nächste zulässige Schritt nach erfolgreicher Acceptance und Schuldenprüfung ist `SM-P3-02`; Renderer und ZBM-Mutation bleiben gesperrt.

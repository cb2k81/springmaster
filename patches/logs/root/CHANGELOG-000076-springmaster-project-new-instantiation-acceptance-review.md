# CHANGELOG 000076 – springmaster project-new instantiation acceptance review

## Zweck

Validiert und härtet die Fähigkeit von Springmaster, ein neues technisches Java-Backend-Skeleton über `project-new.sh` zu instanziieren.

## Änderungen

* `bin/project-new.sh` rendert DBTool-Defaults in kopierten Tooling-Dateien mit sanitisierten DB-Token.
* `bin/project-new-acceptance.sh` ergänzt einen reproduzierbaren Instanziierungs-Acceptance-Lauf.
* `ProjectNewInstantiationAcceptanceTest` bindet den Acceptance-Lauf in Maven-Tests ein.
* `PROJECT_DOCS/TOOLING/PROJECT_NEW_INSTANTIATION_ACCEPTANCE_REVIEW.md` dokumentiert Ergebnis, Grenzen und Freigabeentscheidung.
* Tooling-/Versionierungsdokumente werden auf den neuen Stand fortgeschrieben.

## Validierung

Erwartet:

* Shell-/Python-Syntax OK
* `bin/project-new-acceptance.sh --generated-maven-test` OK
* `mvn -q test` OK
* `mvn -q -Pspringmaster-gates-report test` OK
* Full-ZIP-Export OK

## Version

* `PLATFORM_VERSION=0.13.37-foundation`
* `PLATFORM_TOOLING_VERSION=0.3.11`
* `PLATFORM_DEMO_VERSION=0.2.3`
* `PLATFORM_STATE_PATCH=000076_springmaster_project_new_instantiation_acceptance_review`

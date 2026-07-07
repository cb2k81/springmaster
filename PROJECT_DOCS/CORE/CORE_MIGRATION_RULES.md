# Platform Core Migration Rules

## 1. Zweck

Diese Regeln steuern die spätere Migration von IDM-System-Core-Bausteinen in den kanonischen, an Zielprojekte verteilbaren Core-Namespace `de.cocondo.system`.

Die Springmaster-Anwendung selbst bleibt unter `de.cocondo.platform.app`. Demo-Code bleibt unter `de.cocondo.platform.demo`. Der wiederverwendbare Core wird im Masterprojekt bewusst in demselben Java-Package geführt, das auch in Zielprojekten verwendet werden soll.

## 2. Namespace-Entscheidung

Verbindliche Entscheidung ab Patch `000007`:

| Rolle | Paketwurzel | Zweck |
|---|---|---|
| Springmaster-App | `de.cocondo.platform.app` | ausführbare Master-/Demo-Anwendung |
| Springmaster-Demo | `de.cocondo.platform.demo` | lokale Validierung des Core durch Demo-Fachlichkeit |
| Distributable Core | `de.cocondo.system` | identischer Core-Namespace in Master und Zielprojekten |
| IDM-Referenzquelle | `de.cocondo.app.system` | historische Quelle für die initiale Migration |

Begründung:

* Core-Updates sollen später als Quellcode-Patches in Zielprojekte übertragen werden.
* Identische Package- und Pfadstruktur im Master und im Ziel reduziert Mapping-, Rewrite- und Import-Risiken.
* Der Master kann trotzdem unter `de.cocondo.platform.*` eigene App- und Demo-Bestandteile führen.
* Legacy-/Referenzpfade aus IDM werden nur bei der initialen Migration transformiert.

## 3. Verbindliche Regeln

1. Kein Code aus `de.cocondo.app.domain.idm` darf in den Platform Core übernommen werden.
2. Jede übernommene Core-Datei muss den Package-Root `de.cocondo.system` verwenden.
3. Interne Imports von `de.cocondo.app.system` müssen auf `de.cocondo.system` umgestellt werden.
4. Core-Code darf nicht unter `de.cocondo.platform.core` angelegt werden.
5. `de.cocondo.platform.*` bleibt Springmaster-App-, Demo- und Master-spezifischem Code vorbehalten.
6. Jeder Code-Patch muss klein genug sein, dass Fehler eindeutig einem Slice zugeordnet werden können.
7. Jeder Code-Patch muss mindestens `mvn test` bestehen.
8. Für jeden übernommenen Baustein ist mindestens ein direkter oder indirekter Test erforderlich.
9. Neue Maven-Dependencies dürfen nur explizit und begründet ergänzt werden.
10. Lombok darf nicht stillschweigend eingeführt werden; entweder dependency-bewusst erlauben oder pro Datei manuell ersetzen.
11. JPA-/Repository-/Security-/JWT-Bausteine werden nicht zusammen mit Basic-Core-Typen migriert.
12. Demo-Code bleibt außerhalb des Core und wird unter `de.cocondo.platform.demo` geführt.

## 4. Empfohlene Migrationsreihenfolge

| Schritt | Inhalt | Zulässige Änderung |
|---|---|---|
| 000007 | Core Namespace Strategy | Dokumentations-/Manifestkorrektur; keine Java-Code-Migration |
| 000008 | Basic Core Types | DTO-/ID-/Validation-/Exception-Basistypen, kleine Tests |
| 000009 | Core Dependency Policy | explizite Entscheidung zu Lombok, JPA, Security, JWT |
| 000010 | Persistence Foundation | Entity-/Auditing-/Repository-nahe Basisklassen plus Tests |
| 000011 | Event Foundation | Domain-/Error-Event-Bausteine plus Tests |
| 000012 | Web Infrastructure | HTTP/Error/Info/Swagger-Bausteine plus Controller-Tests |
| später | Security Foundation | Authorization/JWT/Security-Konfiguration als eigener Architektur-Slice |

## 5. Abbruchkriterien

Eine Migration wird abgebrochen, wenn:

* ein IDM-Domain-Import erforderlich wäre,
* eine nicht dokumentierte Dependency nötig wird,
* ein Build- oder Testfehler entsteht,
* ein Patch mehrere nicht zusammenhängende Core-Slices mischt,
* die Zielpaketstruktur nicht eindeutig aus der Klassifikation ableitbar ist,
* Core-Code versehentlich unter `de.cocondo.platform.core` angelegt würde.

package de.cocondo.platform.tooling;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

class SpringmasterGeneratedSliceSpecFixtureGateTest {

    private static final Duration PROCESS_TIMEOUT = Duration.ofSeconds(60);
    private static final String GOLDEN_SPEC =
            "PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml";

    private final Path projectRoot = Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();

    @Test
    void generatedSliceSpecFixtureGateProducesGoldenBusinessPartnerEvidenceWithoutFindings() throws Exception {
        Path report = projectRoot.resolve("target/generated-slice-spec-fixture-gate-test.json");
        Files.deleteIfExists(report);

        ProcessResult result = runCommand(
                "bash",
                "bin/generated-slice-spec-fixture-gate-report.sh",
                "--out",
                "target/generated-slice-spec-fixture-gate-test.json",
                "--generated-at",
                "2026-07-14T00:00:00Z"
        );

        assertThat(result.exitCode())
                .as(result.diagnostic())
                .isZero();
        assertThat(report).isRegularFile();

        Path golden = projectRoot.resolve(
                "src/test/resources/tooling/generated-slice-spec-fixture-gate.business-partner.golden.json"
        );
        assertThat(golden).isRegularFile();

        String json = Files.readString(report, StandardCharsets.UTF_8);
        String expected = Files.readString(golden, StandardCharsets.UTF_8);

        assertThat(json).isEqualTo(expected);
        assertThat(json)
                .contains("\"schemaVersion\": \"springmaster.generated-slice-spec-fixture-gate-report.v1\"")
                .contains("\"mode\": \"strict-fixture-gate\"")
                .contains("\"findings\": 0")
                .contains("\"status\": \"PASS\"")
                .contains("administration.business-partner")
                .contains("GET /api/administration/business-partners/all")
                .contains("GET /api/administration/business-partners/count")
                .contains("BusinessPartnerCreateDTO")
                .contains("BusinessPartnerUpdateDTO")
                .contains("\"400\": [")
                .contains("\"404\": [")
                .contains("\"409\": [")
                .contains("requestValidationOpenApiGate")
                .contains("\"outputMode\": \"patch-zip\"")
                .contains("\"targetApply\": \"forbidden-in-springmaster\"");
    }

    @Test
    void generatedSliceSpecFixtureGateFailsClosedForContractViolations() throws Exception {
        String source = Files.readString(projectRoot.resolve(GOLDEN_SPEC), StandardCharsets.UTF_8);

        List<NegativeCase> cases = List.of(
                new NegativeCase(
                        "missing-reports",
                        source.replaceFirst("(?m)^reports:$", "reportSet:"),
                        "SPEC-TOPLEVEL-001"
                ),
                new NegativeCase(
                        "demo-module-package",
                        source.replace(
                                "modulePackage: de.cocondo.platform.administration.businesspartner",
                                "modulePackage: de.cocondo.platform.demo.businesspartner"
                        ),
                        "SPEC-PACKAGE-005"
                ),
                new NegativeCase(
                        "delete-request-body",
                        source.replace("requestBody: forbidden", "requestBody: optional"),
                        "SPEC-WRITE-004"
                ),
                new NegativeCase(
                        "missing-409-family",
                        source.replace("- status: 409", "- status: 422"),
                        "SPEC-ERROR-006"
                ),
                new NegativeCase(
                        "unsupported-flow-yaml",
                        source.replace(
                                "forbiddenPackagePrefixes:\n    - de.cocondo.platform.demo",
                                "forbiddenPackagePrefixes: [de.cocondo.platform.demo]"
                        ),
                        "SPEC-PARSE-003"
                )
        );

        for (NegativeCase negativeCase : cases) {
            Path spec = projectRoot.resolve("target/generated-slice-spec-negative-" + negativeCase.name() + ".yaml");
            Path report = projectRoot.resolve("target/generated-slice-spec-negative-" + negativeCase.name() + ".json");
            Files.createDirectories(spec.getParent());
            Files.writeString(spec, negativeCase.yaml(), StandardCharsets.UTF_8);
            Files.deleteIfExists(report);

            ProcessResult result = runCommand(
                    "bash",
                    "bin/generated-slice-spec-fixture-gate-report.sh",
                    "--spec",
                    projectRoot.relativize(spec).toString(),
                    "--out",
                    projectRoot.relativize(report).toString(),
                    "--generated-at",
                    "2026-07-14T00:00:00Z"
            );

            assertThat(result.exitCode())
                    .as(negativeCase.name() + System.lineSeparator() + result.diagnostic())
                    .isNotZero();
            assertThat(report).isRegularFile();
            assertThat(Files.readString(report, StandardCharsets.UTF_8))
                    .contains("\"status\": \"FAIL\"")
                    .contains(negativeCase.expectedFindingId());
        }
    }

    private ProcessResult runCommand(String... command) throws IOException, InterruptedException {
        ProcessBuilder processBuilder = new ProcessBuilder(command);
        processBuilder.directory(projectRoot.toFile());
        processBuilder.redirectErrorStream(true);
        Process process = processBuilder.start();
        boolean finished = process.waitFor(PROCESS_TIMEOUT.toSeconds(), TimeUnit.SECONDS);
        String output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        if (!finished) {
            process.destroyForcibly();
            throw new AssertionError(
                    "Process timed out after " + PROCESS_TIMEOUT + ": " + Arrays.toString(command) + "\n" + output
            );
        }
        return new ProcessResult(process.exitValue(), String.join(" ", command), output);
    }

    private record NegativeCase(String name, String yaml, String expectedFindingId) {
    }

    private record ProcessResult(int exitCode, String command, String output) {
        private String diagnostic() {
            List<String> lines = new ArrayList<>();
            lines.add("Command: " + command);
            lines.add("Exit: " + exitCode);
            lines.add("Output:");
            lines.add(output);
            return String.join(System.lineSeparator(), lines);
        }
    }
}

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

class SpringmasterDetailLookupContractReportTest {

    private static final Duration PROCESS_TIMEOUT = Duration.ofSeconds(60);
    private final Path projectRoot = Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();

    @Test
    void detailLookupContractReportProducesCatalogItemGoldenEvidenceWithoutFindings() throws Exception {
        Path report = projectRoot.resolve("target/detail-lookup-contract-gate-report-test.json");
        Files.deleteIfExists(report);

        ProcessResult result = runCommand(
                "bash",
                "bin/detail-lookup-contract-gate-report.sh",
                "--out",
                "target/detail-lookup-contract-gate-report-test.json",
                "--generated-at",
                "2026-07-14T00:00:00Z"
        );

        assertThat(result.exitCode())
                .as(result.diagnostic())
                .isZero();
        assertThat(report).isRegularFile();

        Path golden = projectRoot.resolve("src/test/resources/tooling/detail-lookup-contract-report.catalogitem.golden.json");
        assertThat(golden).isRegularFile();

        String json = Files.readString(report, StandardCharsets.UTF_8);
        String expected = Files.readString(golden, StandardCharsets.UTF_8);

        assertThat(json).isEqualTo(expected);
        assertThat(json)
                .contains("\"schemaVersion\": \"springmaster.detail-lookup-contract-gate-report.v1\"")
                .contains("\"generatedAt\": \"2026-07-14T00:00:00Z\"")
                .contains("\"findings\": 0")
                .contains("GET /api/demo/catalog/items/{id}")
                .contains("GET /api/demo/catalog/items/by-sku/{sku}")
                .contains("\"errorType\": \"RESOURCE_NOT_FOUND\"")
                .contains("\"createLocationDetailConsistency\": \"present\"");
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
            throw new AssertionError("Process timed out after " + PROCESS_TIMEOUT + ": " + Arrays.toString(command) + "\n" + output);
        }
        return new ProcessResult(process.exitValue(), String.join(" ", command), output);
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

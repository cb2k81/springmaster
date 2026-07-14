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
import org.junit.jupiter.api.Test;

class SpringmasterWriteApiContractReportTest {

    private static final Duration PROCESS_TIMEOUT = Duration.ofSeconds(30);

    private final Path projectRoot = Path.of("").toAbsolutePath().normalize();

    @Test
    void generatesCatalogItemWriteApiContractReportGoldenFixture() throws Exception {
        Path report = projectRoot.resolve("target/write-api-contract-report-test.json");
        Files.deleteIfExists(report);

        ProcessResult result = runCommand(
                "bash",
                "bin/write-api-contract-gate-report.sh",
                "--out",
                report.toString(),
                "--generated-at",
                "2026-07-14T00:00:00Z"
        );

        assertThat(result.exitCode())
                .as(result.diagnostic())
                .isZero();
        assertThat(report).isRegularFile();

        Path golden = projectRoot.resolve("src/test/resources/tooling/write-api-contract-report.catalogitem.golden.json");
        assertThat(golden).isRegularFile();

        String json = Files.readString(report, StandardCharsets.UTF_8);
        String expected = Files.readString(golden, StandardCharsets.UTF_8);

        assertThat(json).isEqualTo(expected);
        assertThat(json)
                .contains("\"schemaVersion\": \"springmaster.write-api-contract-gate-report.v1\"")
                .contains("\"generatedAt\": \"2026-07-14T00:00:00Z\"")
                .contains("\"findings\": 0")
                .contains("POST /api/demo/catalog/items")
                .contains("PUT /api/demo/catalog/items/{id}")
                .contains("DELETE /api/demo/catalog/items/{id}")
                .contains("\"status\": 201")
                .contains("\"status\": 204")
                .contains("\"deleteRequestBody\": \"absent\"")
                .contains("\"errorType\": \"CONFLICT\"")
                .contains("\"errorType\": \"RESOURCE_NOT_FOUND\"");
    }

    private ProcessResult runCommand(String... command) throws IOException, InterruptedException {
        ProcessBuilder processBuilder = new ProcessBuilder(command);
        processBuilder.directory(projectRoot.toFile());
        processBuilder.redirectErrorStream(true);
        Process process = processBuilder.start();
        boolean finished = process.waitFor(PROCESS_TIMEOUT.toSeconds(), java.util.concurrent.TimeUnit.SECONDS);
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

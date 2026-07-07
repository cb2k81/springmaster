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

class SpringmasterGatesReportProfileTest {

    private static final Duration PROCESS_TIMEOUT = Duration.ofSeconds(90);
    private final Path projectRoot = Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();

    @Test
    void regressionScriptValidatesReportOnlyGateShapeAndSafetyRules() throws Exception {
        ProcessResult result = runCommand("bash", "bin/springmaster-gates-regression.sh", "000069-junit-regression");

        assertThat(result.exitCode())
                .as(result.diagnostic())
                .isZero();
        assertThat(result.output()).contains("Springmaster report-only gate regression passed");
    }

    @Test
    void mavenProfileRunsReportOnlyGateWithoutTreatingFindingsAsBuildFailures() throws Exception {
        boolean enabled = Boolean.parseBoolean(System.getProperty("springmaster.gates.report.enabled", "false"));
        if (!enabled) {
            return;
        }

        String runId = System.getProperty("springmaster.gates.report.runId", "maven-profile");
        ProcessResult result = runCommand("bash", "bin/springmaster-gates.sh", "report", "--run-id", runId, "--clean");

        assertThat(result.exitCode())
                .as(result.diagnostic())
                .isZero();

        Path reportDir = projectRoot.resolve("target/springmaster-gates").resolve(runId);
        assertThat(reportDir.resolve("summary.txt")).isRegularFile();
        assertThat(reportDir.resolve("summary.json")).isRegularFile();
        assertThat(reportDir.resolve("findings.jsonl")).isRegularFile();
        assertThat(reportDir.resolve("rule-sources.json")).isRegularFile();
        assertThat(reportDir.resolve("input-manifest.json")).isRegularFile();

        String summaryJson = Files.readString(reportDir.resolve("summary.json"), StandardCharsets.UTF_8);
        assertThat(summaryJson)
                .contains("\"reportSchemaVersion\": \"springmaster.report-only-report.v1\"")
                .contains("\"seedId\": \"springmaster.report-only-gate-seed.v1\"")
                .contains("\"mode\": \"report-only\"")
                .contains("\"scope\": \"springmaster-reference-only\"")
                .contains("\"status\": \"SUCCESS\"");

        String findings = Files.readString(reportDir.resolve("findings.jsonl"), StandardCharsets.UTF_8);
        assertThat(findings)
                .contains("SM-G0-RULE-SOURCE-COVERAGE")
                .doesNotContain("SM-G5-CATALOG-READINESS-EVIDENCE");

        String inputManifest = Files.readString(reportDir.resolve("input-manifest.json"), StandardCharsets.UTF_8);
        assertThat(inputManifest)
                .contains("\"catalogDemoEvidence\"")
                .contains("\"sliceState\": \"candidate-reference-slice\"")
                .contains("\"canonicalState\": \"not-canonical\"");
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



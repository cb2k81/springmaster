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

class SpringmasterPatchArtifactPreflightTest {

    private static final Duration PROCESS_TIMEOUT = Duration.ofSeconds(180);
    private final Path projectRoot = Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();

    @Test
    void artifactPreflightPassesInIsolatedTestCopyAndFailsClosedForKnownDefects() throws Exception {
        ProcessResult result = runCommand("bash", "bin/patch-artifact-preflight-it.sh");

        assertThat(result.exitCode())
                .as(result.diagnostic())
                .isZero();
        assertThat(result.output())
                .contains("PATCH_ARTIFACT_PREFLIGHT_IT=PASS")
                .contains("GIT_MODE_CONTRACT=PASS")
                .contains("LOG_DIR=");
    }

    @Test
    void exportIntegrityManifestUsesRawRepositoryBytesAndRejectsTampering() throws Exception {
        ProcessResult result = runCommand("bash", "bin/export-integrity-it.sh");

        assertThat(result.exitCode())
                .as(result.diagnostic())
                .isZero();
        assertThat(result.output())
                .contains("EXPORT_INTEGRITY_IT=PASS")
                .contains("LOG_DIR=");
    }

    private ProcessResult runCommand(String... command) throws IOException, InterruptedException {
        Path outputFile = Files.createTempFile("springmaster-artifact-preflight-test-", ".log");
        try {
            ProcessBuilder processBuilder = new ProcessBuilder(command);
            processBuilder.directory(projectRoot.toFile());
            processBuilder.redirectErrorStream(true);
            processBuilder.redirectOutput(outputFile.toFile());
            Process process = processBuilder.start();
            boolean finished = process.waitFor(PROCESS_TIMEOUT.toSeconds(), TimeUnit.SECONDS);
            if (!finished) {
                process.destroyForcibly();
                process.waitFor(10, TimeUnit.SECONDS);
            }
            String output = Files.readString(outputFile, StandardCharsets.UTF_8);
            if (!finished) {
                throw new AssertionError(
                        "Process timed out after " + PROCESS_TIMEOUT + ": " + Arrays.toString(command) + "\n" + output
                );
            }
            return new ProcessResult(process.exitValue(), String.join(" ", command), output);
        } finally {
            Files.deleteIfExists(outputFile);
        }
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

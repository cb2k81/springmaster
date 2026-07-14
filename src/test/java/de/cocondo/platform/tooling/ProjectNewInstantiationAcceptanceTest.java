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

class ProjectNewInstantiationAcceptanceTest {

    private static final Duration PROCESS_TIMEOUT = Duration.ofSeconds(120);
    private final Path projectRoot = Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();

    @Test
    void projectNewCanInstantiateAndValidateMinimalBackendSkeleton() throws Exception {
        ProcessResult result = runCommand("bash", "bin/project-new-acceptance.sh", "--skip-generated-maven-test");

        assertThat(result.exitCode())
                .as(result.diagnostic())
                .isZero();
        assertThat(result.output()).contains("Project-New instantiation acceptance passed");

        Path generated = projectRoot.resolve("target/project-new-acceptance/sample-backend");
        assertThat(generated.resolve("pom.xml")).isRegularFile();
        assertThat(generated.resolve("bin/patch.sh")).isRegularFile();
        assertThat(generated.resolve("bin/patch-artifact-preflight.py")).isRegularFile();
        assertThat(generated.resolve("bin/patch-artifact-preflight-it.sh")).isRegularFile();
        assertThat(generated.resolve("bin/export.sh")).isRegularFile();
        assertThat(generated.resolve("bin/export-integrity-check.py")).isRegularFile();
        assertThat(generated.resolve("bin/export-integrity-it.sh")).isRegularFile();
        assertThat(generated.resolve("bin/dbtool.sh")).isRegularFile();
        assertThat(generated.resolve("platform/versions/platform.env")).isRegularFile();
        assertThat(generated.resolve(".env")).doesNotExist();

        String generatedExportConfig = Files.readString(generated.resolve("export.config.json"), StandardCharsets.UTF_8);
        assertThat(generatedExportConfig).contains("patches/logs/validation/**");

        String generatedExporter = Files.readString(generated.resolve("bin/export.sh"), StandardCharsets.UTF_8);
        String generatedPreflight = Files.readString(generated.resolve("bin/patch-artifact-preflight.py"), StandardCharsets.UTF_8);
        assertThat(generatedExporter).contains("springmaster.export-closure-evidence.v1");
        assertThat(generatedPreflight)
                .contains("springmaster.patch-artifact-preflight.v1")
                .contains("springmaster.patch-export-evidence.v1");

        String envDefaults = Files.readString(generated.resolve("bin/lib/core/env.sh"), StandardCharsets.UTF_8);
        assertThat(envDefaults)
                .contains("APP_DEV_DB_NAME=\"${APP_DEV_DB_NAME:-sample_backend}\"")
                .contains("APP_DEV_DB_USER=\"${APP_DEV_DB_USER:-sample_backend}\"")
                .contains("APP_STAGE_DB_NAME=\"${APP_STAGE_DB_NAME:-${APP_BUILD_DB_NAME:-sample_backend_build}}\"");
    }

    private ProcessResult runCommand(String... command) throws IOException, InterruptedException {
        Path outputFile = Files.createTempFile("springmaster-project-new-test-", ".log");
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

package de.cocondo.platform.tooling;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class SpringmasterGeneratedSlicePatchBlueprintDryRunTest {

    private static final Duration PROCESS_TIMEOUT = Duration.ofSeconds(60);
    private static final String GOLDEN_IR =
            "src/test/resources/tooling/generated-slice-ir.business-partner.golden.json";
    private static final String GOLDEN_BLUEPRINT =
            "src/test/resources/tooling/generated-slice-patch-blueprint.business-partner.golden.json";
    private static final List<String> REQUIRED_SECTIONS = List.of(
            "schemaVersion",
            "source",
            "projection",
            "patch",
            "artifacts",
            "apiOperations",
            "tests",
            "reports",
            "delivery",
            "blockers",
            "summary"
    );

    private final Path projectRoot = Path.of("").toAbsolutePath().normalize();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void businessPartnerIrProducesTheCanonicalNonMutatingBlueprint() throws Exception {
        Path actual = projectRoot.resolve("target/generated-slice-patch-blueprint.business-partner.actual.json");
        Files.deleteIfExists(actual);
        String statusBefore = gitStatus();

        ProcessResult result = runCommand(
                "business-partner",
                "bash",
                "bin/generated-slice-patch-blueprint.sh",
                "--out",
                projectRoot.relativize(actual).toString()
        );

        assertThat(result.exitCode()).as(result.diagnostic()).isZero();
        assertThat(actual).isRegularFile();
        assertThat(Files.readAllBytes(actual))
                .isEqualTo(Files.readAllBytes(projectRoot.resolve(GOLDEN_BLUEPRINT)));
        assertThat(gitStatus()).isEqualTo(statusBefore);

        JsonNode blueprint = objectMapper.readTree(actual.toFile());
        List<String> actualSections = new ArrayList<>();
        blueprint.fieldNames().forEachRemaining(actualSections::add);
        assertThat(actualSections).containsExactlyElementsOf(REQUIRED_SECTIONS);
        assertThat(blueprint.path("schemaVersion").asText())
                .isEqualTo("springmaster.generated-service-slice-patch-blueprint.v1");
        assertThat(blueprint.path("source").path("sliceId").asText())
                .isEqualTo("administration.business-partner");
        assertThat(blueprint.path("projection").path("targetModulePackageTemplate").asText())
                .isEqualTo("${targetBasePackage}.administration.businesspartner");
        assertThat(blueprint.path("patch").path("scope").asText()).isEqualTo("root");
        assertThat(blueprint.path("patch").path("mutationMode").asText()).isEqualTo("dry-run-only");
        assertThat(blueprint.path("artifacts")).hasSize(15);
        assertThat(blueprint.path("apiOperations")).hasSize(8);
        assertThat(blueprint.path("reports")).hasSize(4);
        assertThat(blueprint.path("blockers")).hasSize(5);
        assertThat(blueprint.path("summary").path("plannedJavaSources").asInt()).isEqualTo(9);
        assertThat(blueprint.path("summary").path("plannedJavaTests").asInt()).isEqualTo(4);
        assertThat(blueprint.path("summary").path("targetFilesWritten").asInt()).isZero();
        assertThat(blueprint.path("summary").path("patchArchivesWritten").asInt()).isZero();
        assertThat(blueprint.path("delivery").path("targetMutation").asText()).isEqualTo("forbidden");
        assertThat(blueprint.path("delivery").path("sourceRendering").asText())
                .isEqualTo("forbidden-in-000126");
        assertThat(blueprint.path("delivery").path("patchArchiveGeneration").asText())
                .isEqualTo("forbidden-in-000126");

        for (JsonNode artifact : blueprint.path("artifacts")) {
            assertThat(artifact.path("state").asText()).isEqualTo("planned-not-rendered");
            assertThat(artifact.path("pathTemplate").asText())
                    .doesNotContain("de/cocondo/platform/demo")
                    .doesNotContain("catalogitem");
        }
    }

    @Test
    void blueprintGenerationIsByteDeterministicAndCreatesNoPatchArchive() throws Exception {
        Path first = projectRoot.resolve("target/generated-slice-patch-blueprint.deterministic-1.json");
        Path second = projectRoot.resolve("target/generated-slice-patch-blueprint.deterministic-2.json");
        Files.deleteIfExists(first);
        Files.deleteIfExists(second);
        long zipCountBefore = countTargetZipFiles();
        String statusBefore = gitStatus();

        ProcessResult firstResult = runCommand(
                "deterministic-1",
                "bash",
                "bin/generated-slice-patch-blueprint.sh",
                "--out",
                projectRoot.relativize(first).toString()
        );
        ProcessResult secondResult = runCommand(
                "deterministic-2",
                "bash",
                "bin/generated-slice-patch-blueprint.sh",
                "--out",
                projectRoot.relativize(second).toString()
        );

        assertThat(firstResult.exitCode()).as(firstResult.diagnostic()).isZero();
        assertThat(secondResult.exitCode()).as(secondResult.diagnostic()).isZero();
        assertThat(Files.readAllBytes(first)).isEqualTo(Files.readAllBytes(second));
        assertThat(gitStatus()).isEqualTo(statusBefore);
        assertThat(countTargetZipFiles()).isEqualTo(zipCountBefore);
    }

    @Test
    void blueprintProjectionIsNotLockedToBusinessPartnerCatalogItemOrPlatformPackage() throws Exception {
        String source = Files.readString(projectRoot.resolve(GOLDEN_IR), StandardCharsets.UTF_8)
                .replace("administration.business-partner", "masterdata.supplier")
                .replace(
                        "de.cocondo.platform.administration.businesspartner",
                        "de.cocondo.platform.masterdata.supplier"
                )
                .replace("/api/administration/business-partners", "/api/masterdata/suppliers")
                .replace("\"domain\": \"administration\"", "\"domain\": \"masterdata\"")
                .replace("\"name\": \"businessPartner\"", "\"name\": \"supplier\"")
                .replace("\"collection\": \"businessPartners\"", "\"collection\": \"suppliers\"")
                .replace("BusinessPartner", "Supplier");

        Path ir = projectRoot.resolve("target/generated-slice-ir.supplier-for-blueprint.json");
        Path out = projectRoot.resolve("target/generated-slice-patch-blueprint.supplier.json");
        Files.createDirectories(ir.getParent());
        Files.writeString(ir, source, StandardCharsets.UTF_8);
        Files.deleteIfExists(out);

        ProcessResult result = runCommand(
                "supplier",
                "bash",
                "bin/generated-slice-patch-blueprint.sh",
                "--ir",
                projectRoot.relativize(ir).toString(),
                "--out",
                projectRoot.relativize(out).toString()
        );

        assertThat(result.exitCode()).as(result.diagnostic()).isZero();
        JsonNode blueprint = objectMapper.readTree(out.toFile());
        assertThat(blueprint.path("source").path("sliceId").asText()).isEqualTo("masterdata.supplier");
        assertThat(blueprint.path("projection").path("modulePackageSuffix").asText())
                .isEqualTo("masterdata.supplier");
        assertThat(blueprint.path("projection").path("targetModulePackageTemplate").asText())
                .isEqualTo("${targetBasePackage}.masterdata.supplier");
        assertThat(blueprint.path("apiOperations").get(0).path("path").asText())
                .isEqualTo("/api/masterdata/suppliers");

        String blueprintText = Files.readString(out, StandardCharsets.UTF_8);
        assertThat(blueprintText)
                .doesNotContain("BusinessPartner")
                .doesNotContain("/api/demo/")
                .doesNotContain("src/main/java/de/cocondo/platform/");
    }

    @Test
    void invalidIrFailsClosedWithoutBlueprintOutput() throws Exception {
        String source = Files.readString(projectRoot.resolve(GOLDEN_IR), StandardCharsets.UTF_8);
        List<NegativeCase> cases = List.of(
                new NegativeCase(
                        "unsupported-schema",
                        source.replace(
                                "springmaster.generated-service-slice-ir.v1",
                                "springmaster.generated-service-slice-ir.v2"
                        ),
                        "unsupported IR schema"
                ),
                new NegativeCase(
                        "module-outside-base",
                        source.replace(
                                "de.cocondo.platform.administration.businesspartner",
                                "org.example.businesspartner"
                        ),
                        "module package must be below"
                ),
                new NegativeCase(
                        "optional-report",
                        source.replaceFirst(
                                "\"queryContract\": \"required\"",
                                "\"queryContract\": \"optional\""
                        ),
                        "report contract must remain required"
                ),
                new NegativeCase(
                        "target-apply-enabled",
                        source.replace(
                                "\"targetApply\": \"forbidden-in-springmaster\"",
                                "\"targetApply\": \"allowed\""
                        ),
                        "IR validation failed"
                )
        );

        for (NegativeCase negativeCase : cases) {
            Path ir = projectRoot.resolve("target/generated-slice-blueprint-negative-" + negativeCase.name() + ".json");
            Path out = projectRoot.resolve("target/generated-slice-blueprint-negative-" + negativeCase.name() + ".out.json");
            Files.writeString(ir, negativeCase.ir(), StandardCharsets.UTF_8);
            Files.deleteIfExists(out);

            ProcessResult result = runCommand(
                    "negative-" + negativeCase.name(),
                    "bash",
                    "bin/generated-slice-patch-blueprint.sh",
                    "--ir",
                    projectRoot.relativize(ir).toString(),
                    "--out",
                    projectRoot.relativize(out).toString()
            );

            assertThat(result.exitCode())
                    .as(negativeCase.name() + System.lineSeparator() + result.diagnostic())
                    .isNotZero();
            assertThat(result.output()).contains(negativeCase.expectedDiagnostic());
            assertThat(out).doesNotExist();
        }
    }

    @Test
    void toolHasAnIrOnlyInputSurface() throws Exception {
        String tool = Files.readString(
                projectRoot.resolve("bin/generated-slice-patch-blueprint.py"),
                StandardCharsets.UTF_8
        );
        assertThat(tool)
                .contains("--ir")
                .doesNotContain("--spec")
                .doesNotContain("DEFAULT_SPEC")
                .doesNotContain("GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER")
                .doesNotContain("zipfile.ZipFile")
                .doesNotContain("subprocess.run")
                .doesNotContain("src/main/java/de/cocondo/platform/demo");
    }

    private String gitStatus() throws IOException, InterruptedException {
        ProcessResult result = runCommand(
                "git-status-" + System.nanoTime(),
                "git",
                "status",
                "--porcelain=v1",
                "--untracked-files=all"
        );
        assertThat(result.exitCode()).as(result.diagnostic()).isZero();
        return result.output();
    }

    private long countTargetZipFiles() throws IOException {
        Path target = projectRoot.resolve("target");
        if (!Files.isDirectory(target)) {
            return 0L;
        }
        try (Stream<Path> paths = Files.walk(target)) {
            return paths.filter(Files::isRegularFile)
                    .filter(path -> path.getFileName().toString().endsWith(".zip"))
                    .count();
        }
    }

    private ProcessResult runCommand(String name, String... command) throws IOException, InterruptedException {
        Path outputFile = projectRoot.resolve("target/generated-slice-blueprint-process-" + name + ".log");
        Files.createDirectories(outputFile.getParent());
        Files.deleteIfExists(outputFile);

        ProcessBuilder processBuilder = new ProcessBuilder(command);
        processBuilder.directory(projectRoot.toFile());
        processBuilder.redirectErrorStream(true);
        processBuilder.redirectOutput(outputFile.toFile());
        Process process = processBuilder.start();
        boolean finished = process.waitFor(PROCESS_TIMEOUT.toSeconds(), TimeUnit.SECONDS);
        if (!finished) {
            process.destroyForcibly();
            process.waitFor(5, TimeUnit.SECONDS);
            throw new AssertionError(
                    "Process timed out after " + PROCESS_TIMEOUT + ": " + Arrays.toString(command)
                            + System.lineSeparator() + readOutput(outputFile)
            );
        }
        return new ProcessResult(
                process.exitValue(),
                String.join(" ", command),
                readOutput(outputFile)
        );
    }

    private String readOutput(Path path) throws IOException {
        return Files.exists(path) ? Files.readString(path, StandardCharsets.UTF_8) : "";
    }

    private record NegativeCase(String name, String ir, String expectedDiagnostic) {
    }

    private record ProcessResult(int exitCode, String command, String output) {
        private String diagnostic() {
            return "Command: " + command + System.lineSeparator()
                    + "Exit: " + exitCode + System.lineSeparator()
                    + "Output:" + System.lineSeparator()
                    + output;
        }
    }
}

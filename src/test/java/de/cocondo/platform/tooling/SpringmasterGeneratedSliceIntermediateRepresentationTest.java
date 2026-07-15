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
import org.junit.jupiter.api.Test;

class SpringmasterGeneratedSliceIntermediateRepresentationTest {

    private static final Duration PROCESS_TIMEOUT = Duration.ofSeconds(60);
    private static final String GOLDEN_SPEC =
            "PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml";
    private static final String GOLDEN_IR =
            "src/test/resources/tooling/generated-slice-ir.business-partner.golden.json";
    private static final List<String> REQUIRED_SECTIONS = List.of(
            "schemaVersion",
            "source",
            "metadata",
            "packages",
            "resource",
            "query",
            "detail",
            "write",
            "model",
            "validation",
            "errorContract",
            "reports",
            "delivery"
    );

    private final Path projectRoot = Path.of("").toAbsolutePath().normalize();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void businessPartnerSpecProducesTheCanonicalNeutralIr() throws Exception {
        Path actual = projectRoot.resolve("target/generated-slice-ir.business-partner.actual.json");
        Files.deleteIfExists(actual);

        ProcessResult result = runCommand(
                "business-partner",
                "bash",
                "bin/generated-slice-ir.sh",
                "--out",
                projectRoot.relativize(actual).toString()
        );

        assertThat(result.exitCode()).as(result.diagnostic()).isZero();
        assertThat(actual).isRegularFile();
        assertThat(Files.readAllBytes(actual)).isEqualTo(Files.readAllBytes(projectRoot.resolve(GOLDEN_IR)));

        JsonNode ir = objectMapper.readTree(actual.toFile());
        List<String> actualSections = new ArrayList<>();
        ir.fieldNames().forEachRemaining(actualSections::add);
        assertThat(actualSections).containsExactlyElementsOf(REQUIRED_SECTIONS);
        assertThat(ir.path("schemaVersion").asText())
                .isEqualTo("springmaster.generated-service-slice-ir.v1");
        assertThat(ir.path("source").path("sliceId").asText())
                .isEqualTo("administration.business-partner");
        assertThat(ir.path("query").path("operations")).hasSize(3);
        assertThat(ir.path("detail").path("alternateLookups")).hasSize(1);
        assertThat(ir.path("write").path("create").path("requestDto").asText())
                .isEqualTo("BusinessPartnerCreateDTO");
        assertThat(ir.path("write").path("update").path("requestDto").asText())
                .isEqualTo("BusinessPartnerUpdateDTO");
        assertThat(ir.path("validation").path("entitiesAsRequestBody").asText())
                .isEqualTo("forbidden");
        assertThat(ir.path("errorContract").path("statusMappings")).hasSize(3);
        assertThat(ir.path("reports").size()).isEqualTo(4);
        assertThat(ir.path("delivery").path("outputMode").asText()).isEqualTo("patch-zip");

        String modulePackage = ir.path("packages").path("module").asText();
        assertThat(modulePackage).doesNotStartWith("de.cocondo.platform.demo");
        assertThat(ir.path("packages").path("forbiddenPrefixes").toString())
                .contains("de.cocondo.platform.demo");
        assertThat(Files.readString(actual, StandardCharsets.UTF_8).toLowerCase())
                .doesNotContain("catalogitem")
                .doesNotContain("/api/demo/");
    }

    @Test
    void irGenerationIsByteDeterministic() throws Exception {
        Path first = projectRoot.resolve("target/generated-slice-ir.deterministic-1.json");
        Path second = projectRoot.resolve("target/generated-slice-ir.deterministic-2.json");
        Files.deleteIfExists(first);
        Files.deleteIfExists(second);

        ProcessResult firstResult = runCommand(
                "deterministic-1",
                "bash",
                "bin/generated-slice-ir.sh",
                "--out",
                projectRoot.relativize(first).toString()
        );
        ProcessResult secondResult = runCommand(
                "deterministic-2",
                "bash",
                "bin/generated-slice-ir.sh",
                "--out",
                projectRoot.relativize(second).toString()
        );

        assertThat(firstResult.exitCode()).as(firstResult.diagnostic()).isZero();
        assertThat(secondResult.exitCode()).as(secondResult.diagnostic()).isZero();
        assertThat(Files.readAllBytes(first)).isEqualTo(Files.readAllBytes(second));
    }

    @Test
    void transformerIsNotLockedToBusinessPartnerOrDemoPackages() throws Exception {
        String source = Files.readString(projectRoot.resolve(GOLDEN_SPEC), StandardCharsets.UTF_8)
                .replace("administration.business-partner", "masterdata.supplier")
                .replace("catalogitem-pattern-family", "synthetic-neutrality-fixture")
                .replace(
                        "de.cocondo.platform.administration.businesspartner",
                        "de.cocondo.platform.masterdata.supplier"
                )
                .replace("domain: administration", "domain: masterdata")
                .replace("resourceName: businessPartner", "resourceName: supplier")
                .replace("collectionName: businessPartners", "collectionName: suppliers")
                .replace(
                        "basePath: /api/administration/business-partners",
                        "basePath: /api/masterdata/suppliers"
                )
                .replace("BusinessPartner", "Supplier");

        Path spec = projectRoot.resolve("target/generated-slice-spec.supplier.yaml");
        Path out = projectRoot.resolve("target/generated-slice-ir.supplier.json");
        Files.createDirectories(spec.getParent());
        Files.writeString(spec, source, StandardCharsets.UTF_8);
        Files.deleteIfExists(out);

        ProcessResult result = runCommand(
                "supplier",
                "bash",
                "bin/generated-slice-ir.sh",
                "--spec",
                projectRoot.relativize(spec).toString(),
                "--out",
                projectRoot.relativize(out).toString()
        );

        assertThat(result.exitCode()).as(result.diagnostic()).isZero();
        JsonNode ir = objectMapper.readTree(out.toFile());
        assertThat(ir.path("source").path("sliceId").asText()).isEqualTo("masterdata.supplier");
        assertThat(ir.path("packages").path("module").asText())
                .isEqualTo("de.cocondo.platform.masterdata.supplier");
        assertThat(ir.path("resource").path("name").asText()).isEqualTo("supplier");
        assertThat(ir.path("query").path("operations").get(0).path("absolutePath").asText())
                .isEqualTo("/api/masterdata/suppliers");
        assertThat(Files.readString(out, StandardCharsets.UTF_8))
                .doesNotContain("BusinessPartner")
                .doesNotContain("/api/demo/catalog/items");
    }

    @Test
    void invalidOrInconsistentSpecsFailClosedWithoutIrOutput() throws Exception {
        String source = Files.readString(projectRoot.resolve(GOLDEN_SPEC), StandardCharsets.UTF_8);
        List<NegativeCase> cases = List.of(
                new NegativeCase(
                        "demo-package",
                        source.replace(
                                "modulePackage: de.cocondo.platform.administration.businesspartner",
                                "modulePackage: de.cocondo.platform.demo.businesspartner"
                        ),
                        "packageModel.modulePackage"
                ),
                new NegativeCase(
                        "unknown-filter",
                        source.replace("      filters:\n        - code", "      filters:\n        - unknown\n        - code"),
                        "query filter is not backed"
                ),
                new NegativeCase(
                        "missing-reports",
                        source.replaceFirst("(?m)^reports:$", "reportSet:"),
                        "top-level sections"
                )
        );

        for (NegativeCase negativeCase : cases) {
            Path spec = projectRoot.resolve("target/generated-slice-ir-negative-" + negativeCase.name() + ".yaml");
            Path out = projectRoot.resolve("target/generated-slice-ir-negative-" + negativeCase.name() + ".json");
            Files.writeString(spec, negativeCase.yaml(), StandardCharsets.UTF_8);
            Files.deleteIfExists(out);

            ProcessResult result = runCommand(
                    "negative-" + negativeCase.name(),
                    "bash",
                    "bin/generated-slice-ir.sh",
                    "--spec",
                    projectRoot.relativize(spec).toString(),
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

    private ProcessResult runCommand(String name, String... command) throws IOException, InterruptedException {
        Path outputFile = projectRoot.resolve("target/generated-slice-ir-process-" + name + ".log");
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

    private record NegativeCase(String name, String yaml, String expectedDiagnostic) {
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
